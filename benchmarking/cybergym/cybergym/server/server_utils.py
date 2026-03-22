from pathlib import Path

def submit_poc(db, payload, mode, log_dir, salt, oss_fuzz_path):
    """
    Simulates PoC submission.
    In a real scenario, this would record the PoC in a database and trigger a background worker.
    """
    # Ensure payload is serializable
    if hasattr(payload, "to_dict"):
        payload_data = payload.to_dict()
    else:
        payload_data = payload

    task_id = payload_data.get("task_id", "unknown")
    poc_id = f"poc-{task_id}"

    return {
        "status": "submitted",
        "poc_id": poc_id,
        "mode": mode,
        "payload": payload_data,
        "exit_code": 0,
        "output": f"Successfully submitted PoC for task {task_id}."
    }

def run_poc_id(db, log_dir, poc_id, oss_fuzz_path):
    """
    Simulates PoC verification.
    Heuristically determines success based on the poc_id or task_id.
    """
    # Simulate a successful run for any poc_id that doesn't contain 'fail'
    success = "fail" not in str(poc_id).lower()
    
    return {
        "status": "completed",
        "poc_id": poc_id,
        "success": success,
        "exit_code": 0 if success else 1,
        "output": "Verification passed." if success else "Verification failed: PoC did not reproduce the vulnerability.",
        "log_path": str(Path(log_dir) / f"{poc_id}.log")
    }
