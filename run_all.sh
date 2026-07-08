#!/bin/bash
echo "======================================"
echo "🚀 STARTING SUBGOLDEN PIPELINE"
echo "======================================"

python3 step1_fetch.py
python3 step2_post_ids.py
python3 step3_filter.py
python3 step4_extremes.py
python3 step5_frequent.py
python3 step6_golden.py

echo "======================================"
echo "✅ PIPELINE FINISHED"
echo "======================================"
