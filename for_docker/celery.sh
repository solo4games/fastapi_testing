#!/bin/bash

celery -A app.tasks.celery:celery_app worker --loglevel=info