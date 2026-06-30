"""Google Cloud Function entrypoint, triggered by Cloud Scheduler.

Deploy with:
    gcloud functions deploy poll-transcripts \\
        --runtime python312 \\
        --trigger-http \\
        --entry-point poll_transcripts \\
        --region $GCP_REGION \\
        --set-env-vars-file .env.yaml

Cloud Scheduler job (every 2 min):
    gcloud scheduler jobs create http poll-transcripts-job \\
        --schedule="*/2 * * * *" \\
        --uri="https://$GCP_REGION-$GCP_PROJECT_ID.cloudfunctions.net/poll-transcripts" \\
        --http-method=POST
"""
from __future__ import annotations

from pipeline.runner import run_once


def poll_transcripts(request):  # noqa: ARG001 - required Functions Framework signature
    summary = run_once()
    return summary
