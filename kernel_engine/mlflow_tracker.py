import mlflow
import os
from typing import Dict, Any, List
from datetime import datetime

class KernelMLflowTracker:
    """
    Bridges Kernel Cognitive Observations with MLflow Tracking.
    Maps semantic_extension to MLflow metrics and params.
    """
    def __init__(self, tracking_uri: str = None, experiment_name: str = "Agent-Reliability-Audit"):
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def log_theory_identification(self, agent_id: str, run_id: str, identification_action: Dict[str, Any]):
        """
        Logs a theory identification AssessAction to MLflow.
        """
        with mlflow.start_run(run_name=f"Audit-{agent_id}", nested=True):
            # 1. Log identified theories as tags
            ext = identification_action.get("semantic_extension", {})
            theories = ext.get("taxonomy", {}).get("labels", [])
            for theory in theories:
                mlflow.set_tag(f"theory.{theory}", "true")

            # 2. Log Confidence and Bias Scores as metrics
            attrs = ext.get("attributes", {})
            if "bias_score" in attrs:
                mlflow.log_metric("bias_score", attrs["bias_score"])
            
            mlflow.log_metric("identification_confidence", 
                              identification_action.get("result", {}).get("confidence_score", 0.0))

            # 3. Log Lineage and Change Reason as params
            mlflow.log_param("agent_id", agent_id)
            mlflow.log_param("kernel_run_id", run_id)
            mlflow.log_param("change_reason", ext.get("audit_tracking", {}).get("change_reason", "unknown"))

    def log_reliability_metrics(self, agent_id: str, metrics: Dict[str, float]):
        """
        Logs formal Reliability Science metrics (RDC, MOP, VAF).
        """
        with mlflow.start_run(run_name=f"Reliability-{agent_id}", nested=True):
            for name, value in metrics.items():
                mlflow.log_metric(name, value)
            mlflow.set_tag("metric_type", "reliability_science")

if __name__ == "__main__":
    # Example usage for documentation
    tracker = KernelMLflowTracker()
    print("MLflow Tracker initialized for Agent Reliability Audit.")
