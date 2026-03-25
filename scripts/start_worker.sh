#!/usr/bin/env bash
set -euo pipefail

exec celery -A src.worker.celery_app worker "$@"
