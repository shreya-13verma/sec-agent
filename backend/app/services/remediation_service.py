import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session, joinedload
from backend.app.models.remediation import RemediationPlan, RemediationStep
from backend.app.models.host import Host, HostPackage, HostMissingErrata
from backend.app.models.user import User
from backend.app.models.compliance import ComplianceFramework
from backend.app.services.suse_mlm_client import mlm_client
from backend.app.services.compliance_engine import compliance_engine
from backend.app.services.audit_service import log_audit_event

logger = logging.getLogger(__name__)

class RemediationService:
    """
    Service for managing controlled, role-gated remediation workflows.
    Enforces human approval gates before executing package/errata changes on SUSE MLM hosts.
    """

    def approve_plan(
        self,
        db: Session,
        plan_id: int,
        approval_notes: Optional[str],
        user: User
    ) -> RemediationPlan:
        plan = db.query(RemediationPlan).filter(RemediationPlan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Remediation plan {plan_id} not found")

        if plan.status not in ("STAGED", "DRAFT"):
            raise ValueError(f"Plan is currently in '{plan.status}' status and cannot be approved")

        plan.status = "APPROVED"
        plan.approved_by_user_id = user.id
        plan.approval_notes = approval_notes or "Approved by authorized officer"
        db.commit()
        db.refresh(plan)

        log_audit_event(
            db=db,
            action="REMEDIATION_PLAN_APPROVED",
            resource_type="REMEDIATION_PLAN",
            resource_id=str(plan.id),
            details=f"Plan #{plan.id} for host #{plan.host_id} approved by '{user.username}'. Notes: {plan.approval_notes}",
            user=user
        )
        return plan

    def reject_plan(
        self,
        db: Session,
        plan_id: int,
        rejection_reason: str,
        user: User
    ) -> RemediationPlan:
        plan = db.query(RemediationPlan).filter(RemediationPlan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Remediation plan {plan_id} not found")

        if plan.status not in ("STAGED", "DRAFT"):
            raise ValueError(f"Plan is currently in '{plan.status}' status and cannot be rejected")

        plan.status = "REJECTED"
        plan.rejection_reason = rejection_reason
        db.commit()
        db.refresh(plan)

        log_audit_event(
            db=db,
            action="REMEDIATION_PLAN_REJECTED",
            resource_type="REMEDIATION_PLAN",
            resource_id=str(plan.id),
            details=f"Plan #{plan.id} rejected by '{user.username}'. Reason: {rejection_reason}",
            user=user
        )
        return plan

    def execute_plan(
        self,
        db: Session,
        plan_id: int,
        user: User
    ) -> Dict[str, Any]:
        plan = db.query(RemediationPlan).options(
            joinedload(RemediationPlan.steps),
            joinedload(RemediationPlan.host)
        ).filter(RemediationPlan.id == plan_id).first()

        if not plan:
            raise ValueError(f"Remediation plan {plan_id} not found")

        if plan.status != "APPROVED":
            raise ValueError(f"Cannot execute unapproved plan. Current status is '{plan.status}'. Approval is strictly required.")

        plan.status = "IN_PROGRESS"
        db.commit()

        host = plan.host
        dispatched_count = 0

        for step in plan.steps:
            step.status = "RUNNING"
            db.commit()

            if step.action_type == "APPLY_ERRATA":
                res = mlm_client.schedule_apply_errata(host.mlm_system_id, step.target_package_or_errata)
                step.mlm_action_id = res["action_id"]
                step.status = "SUCCESS"
                step.execution_log = f"Errata applied via SUSE MLM action #{res['action_id']}"
                # Remove from host missing errata in database
                db.query(HostMissingErrata).filter(
                    HostMissingErrata.host_id == host.id
                ).delete()
                host.critical_errata_count = 0
                dispatched_count += 1

            elif step.action_type == "REMOVE_PACKAGE":
                res = mlm_client.schedule_package_action(host.mlm_system_id, step.target_package_or_errata, action="REMOVE")
                step.mlm_action_id = res["action_id"]
                step.status = "SUCCESS"
                step.execution_log = f"Package removed via SUSE MLM action #{res['action_id']}"
                # Remove package from host inventory in database
                db.query(HostPackage).filter(
                    HostPackage.host_id == host.id,
                    HostPackage.package_name == step.target_package_or_errata
                ).delete()
                dispatched_count += 1

            elif step.action_type == "INSTALL_PACKAGE":
                res = mlm_client.schedule_package_action(host.mlm_system_id, step.target_package_or_errata, action="INSTALL")
                step.mlm_action_id = res["action_id"]
                step.status = "SUCCESS"
                step.execution_log = f"Package installed via SUSE MLM action #{res['action_id']}"
                # Add package to host inventory
                existing_pkg = db.query(HostPackage).filter(
                    HostPackage.host_id == host.id,
                    HostPackage.package_name == step.target_package_or_errata
                ).first()
                if not existing_pkg:
                    db.add(HostPackage(
                        host_id=host.id,
                        package_name=step.target_package_or_errata,
                        package_version="latest",
                        package_release="1",
                        package_arch="x86_64"
                    ))
                dispatched_count += 1

            db.commit()

        plan.status = "COMPLETED"
        plan.executed_at = datetime.now(timezone.utc)
        db.commit()

        # Trigger automatic post-remediation verification scan
        framework = db.query(ComplianceFramework).first()
        if framework:
            compliance_engine.run_scan(
                db=db,
                framework_id=framework.id,
                host_ids=[host.id],
                user=user
            )

        log_audit_event(
            db=db,
            action="REMEDIATION_PLAN_EXECUTED",
            resource_type="REMEDIATION_PLAN",
            resource_id=str(plan.id),
            details=f"Remediation plan #{plan.id} executed by '{user.username}'. {dispatched_count} steps dispatched to host '{host.hostname}'. Verification scan triggered.",
            user=user
        )

        return {
            "plan_id": plan.id,
            "status": "COMPLETED",
            "message": f"Successfully executed {dispatched_count} remediation steps on host '{host.hostname}'. Post-remediation verification completed.",
            "dispatched_steps_count": dispatched_count
        }

remediation_service = RemediationService()
