
## Setup

In `methods/ReFoRCE` folder, run:
```bash
python spider_agent_setup_snow.py --example_folder examples_snow_sl
python reconstruct_data.py --example_folder examples_snow_sl --add_description --add_sample_rows --rm_digits
```

## Schema Linking by Parsing Generated JSON

Generate prompts by splits:
```bash
python mk_prompt_spider2.py \
  --db_path ../../ReFoRCE/examples_snow_sl \
  --task snow \
  --output_path spider2snow_input.json \
  --tokenizer_name Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --snow_json_path ~/Spider2/spider2-snow/spider2-snow.jsonl
```

Inference:
```bash
export AZURE_ENDPOINT=YOUR_AZURE_ENDPOINT
export AZURE_OPENAI_KEY=YOUR_AZURE_API_KEY
python infer_api.py \
  --deployment_name gpt-4o \
  --api_version 2024-05-01-preview
```

Parse from generated json:
```bash
python parse_json.py \
  --pred_path spider2snow_output.json \
  --gold_path ~/Spider2/methods/gold-tables/spider2-snow-gold-tables.jsonl \
  --snow_json_path ~/Spider2/spider2-snow/spider2-snow.jsonl \
  --db_path ../../ReFoRCE/examples_snow_sl \
  --output_path ../../../data/parsed_json_snow.json
```

## Schema Linking by Parsing Logs

Parse from generation logs:
```bash
python parse_logs.py \
  --ce_paths ~/reforce/methods/ReFoRCE/output/o3-snow-log ~/reforce/methods/ReFoRCE/output/o4-mini-snow-log ~/reforce/methods/ReFoRCE/output/gpt-4o-snow-log \
  --gold_path ~/Spider2/methods/gold-tables/spider2-snow-gold-tables.jsonl \
  --snow_json_path ~/Spider2/spider2-snow/spider2-snow.jsonl \
  --db_path ../../ReFoRCE/examples_snow_sl \
  --output_path ../../../data/parsed_logs_snow.json
```

## Get Reduced Prompts

In `methods/ReFoRCE` folder, run:
```bash
python schema_linking.py --db_path examples_snow_sl --linking_method gen --linked_json_pth ../../data/parsed_logs_snow.json --threshold 0
```