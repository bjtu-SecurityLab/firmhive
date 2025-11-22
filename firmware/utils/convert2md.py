import json
import os
import argparse

def load_knowledge_base(file_path):
    alerts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        alerts.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"Warning: Failed to decode a line, skipped: {line.strip()}")
        return alerts
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        return None

def filter_and_sort_alerts(alerts_list):
    if not alerts_list:
        return [], 0

    def sort_key(finding):
        try:
            risk = float(finding.get('risk_score', 0) or 0)
            confidence = float(finding.get('confidence', 0) or 0)
            return (-risk, -confidence)
        except (ValueError, TypeError):
            placeholder_id = f"{finding.get('file_path', 'N/A')} at {finding.get('location', 'N/A')}"
            print(f"Warning: Invalid values in finding, ranked lowest: {placeholder_id}")
            return (0, 0)

    sorted_alerts = sorted(alerts_list, key=sort_key)
    return sorted_alerts, len(sorted_alerts)

def _format_verification_record_md(record: dict, header_level: int = 3) -> str:
    task = record.get('verification_task', {})
    result_raw = record.get('verification_result', {})
    duration = record.get('verification_duration_seconds', 'N/A')
    tokens = record.get('verification_token_usage', 'N/A')
    
    result_dict = None
    if isinstance(result_raw, str):
        try:
            parsed_result = json.loads(result_raw)
            if isinstance(parsed_result, dict):
                result_dict = parsed_result
        except json.JSONDecodeError: pass
    elif isinstance(result_raw, dict):
        result_dict = result_raw

    header_prefix = '#' * header_level
    markdown_output = f"{header_prefix} Original Information\n\n"
    path_to_display = task.get('file_path') or task.get('dir_path') or task.get('relative_path') or task.get('file_name', 'N/A')
    if path_to_display and path_to_display != 'N/A':
        markdown_output += f"- **File/Directory Path:** `{path_to_display}`\n"
    markdown_output += f"- **Location:** `{task.get('location', 'N/A')}`\n"
    if task.get('description'):
        markdown_output += f"- **Description:** {task.get('description', 'N/A')}\n"
    code_snippet_value = task.get('code_snippet')
    if code_snippet_value:
        processed_snippet_str = "\n".join(str(item) for item in code_snippet_value) if isinstance(code_snippet_value, list) else str(code_snippet_value)
        escaped_snippet = processed_snippet_str.replace('`', '\\`')
        lines = escaped_snippet.splitlines()
        indented_code_block_content = "\n".join([f"  {line}" for line in lines])
        markdown_output += f"- **Code Snippet:**\n  ```\n{indented_code_block_content}\n  ```\n"
    notes = task.get('notes')
    if notes:
        markdown_output += f"- **Notes:** {notes}\n"
    markdown_output += f"\n{header_prefix} Verification Conclusion\n\n"
    if result_dict and 'accuracy' in result_dict and 'vulnerability' in result_dict:
        markdown_output += f"- **Description Accuracy:** `{result_dict.get('accuracy', 'N/A')}`\n"
        markdown_output += f"- **Is Real Vulnerability:** `{result_dict.get('vulnerability', 'N/A')}`\n"
        markdown_output += f"- **Risk Level:** `{result_dict.get('risk_level', 'N/A')}`\n"
        markdown_output += f"- **Detailed Reason:** {result_dict.get('reason', 'N/A')}\n"
    else:
        output_str = json.dumps(result_dict, indent=2, ensure_ascii=False) if result_dict else str(result_raw)
        markdown_output += f"**Raw Verification Result:**\n```json\n{output_str}\n```\n"
    markdown_output += f"\n{header_prefix} Verification Metrics\n\n"
    markdown_output += f"- **Verification Duration:** {float(duration):.2f} s\n" if isinstance(duration, float) else f"- **Verification Duration:** {duration}\n"
    markdown_output += f"- **Token Usage:** {tokens}\n"
    markdown_output += "\n---\n\n"
    return markdown_output

def generate_verification_report_md(output_dir, output_filename="verification_report.md", results_file=None):
    report_title = f"{os.path.basename(os.path.abspath(output_dir))} - Verification Report"
    if results_file is None:
        results_file = os.path.join(output_dir, "verification_results.jsonl")
    
    if not os.path.exists(results_file):
        print(f"Warning: 'verification_results.jsonl' not found in '{output_dir}'.")
        return False, "Verification results file not found"

    all_results = load_knowledge_base(results_file)
    if not all_results:
        markdown_output = f"# {report_title}\n\nVerification results file is empty."
    else:
        filtered_results = []
        for r in all_results:
            try:
                task = r.get('verification_task', {})
                if float(task.get('risk_score', 0) or 0) > 0.5:
                    filtered_results.append(r)
            except (ValueError, TypeError):
                pass
        
        markdown_output = f"# {report_title} ({len(filtered_results)} findings)\n\n"
        markdown_output += "---\n\n"

        if not filtered_results:
             markdown_output += "No verified finding with risk score > 0.5 was found.\n"
        else:
            sorted_results, _ = filter_and_sort_alerts(filtered_results)
            for record in sorted_results:
                markdown_output += _format_verification_record_md(record, header_level=2)
            
    output_markdown_file = os.path.join(output_dir, output_filename)
    try:
        with open(output_markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        return True, output_markdown_file
    except IOError as e:
        return False, f"Failed to write file {output_markdown_file}: {str(e)}"

def convert_to_markdown(alerts, kb_title, total_alerts_count):
    markdown_output = f"# {kb_title} ({total_alerts_count} findings)\n\n"
    markdown_output += "---\n\n"

    if not alerts:
        markdown_output += "No eligible findings with risk score > 0.5 were found.\n"
        return markdown_output

    for finding in alerts:
        name = finding.get('name', 'Untitled Finding')
        markdown_output += f"### {name}\n\n"
        
        path_to_display = finding.get('file_path') or finding.get('dir_path') or finding.get('relative_path') or finding.get('file_name', 'N/A')
        if path_to_display:
            markdown_output += f"- **File/Directory Path:** `{path_to_display}`\n"
        
        markdown_output += f"- **Location:** `{finding.get('location', 'N/A')}`\n"

        markdown_output += f"- **Risk Score:** {finding.get('risk_score', 'N/A')}\n"
        
        markdown_output += f"- **Confidence:** {finding.get('confidence', 'N/A')}\n"
        
        markdown_output += f"- **Description:** {finding.get('description', 'N/A')}\n"
        
        code_snippet_value = finding.get('code_snippet')
        if code_snippet_value:
            processed_snippet_str = "\n".join(str(item) for item in code_snippet_value) if isinstance(code_snippet_value, list) else str(code_snippet_value)
            escaped_snippet = processed_snippet_str.replace('`', '\\`')
            lines = escaped_snippet.splitlines()
            indented_code_block_content = "\n".join([f"  {line}" for line in lines])
            markdown_output += f"- **Code Snippet:**\n  ```\n{indented_code_block_content}\n  ```\n"
            
        link_identifiers = finding.get('link_identifiers') or finding.get('keywords')
        if link_identifiers and isinstance(link_identifiers, list):
            markdown_output += f"- **Keywords:** {', '.join(str(k) for k in link_identifiers)}\n"
            
        notes = finding.get('notes')
        if notes:
            markdown_output += f"- **Notes:** {notes}\n"
            
        markdown_output += "\n---\n"
        
    return markdown_output

def convert_kb_to_markdown(knowledge_base_file_path, output_filename="knowledge_base.md"):
    kb_dir_path = os.path.dirname(knowledge_base_file_path)
    kb_title = os.path.basename(kb_dir_path) if kb_dir_path else "Knowledge Base"
    
    all_alerts = load_knowledge_base(knowledge_base_file_path)
    
    if all_alerts is None:
        return False, f"Failed to load or find knowledge base file: {knowledge_base_file_path}"
    if not all_alerts:
        print(f"Warning: Knowledge base '{knowledge_base_file_path}' is empty. Generating empty report.")
    
    filtered_alerts = []
    for f in all_alerts:
        try:
            if float(f.get('risk_score', 0) or 0) > 0.5:
                filtered_alerts.append(f)
        except (ValueError, TypeError):
            pass

    sorted_alerts, _ = filter_and_sort_alerts(filtered_alerts)
    
    markdown_content = convert_to_markdown(
        sorted_alerts,
        kb_title, 
        len(sorted_alerts)
    )
    
    output_markdown_file = os.path.join(kb_dir_path, output_filename)
    
    try:
        with open(output_markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        return True, output_markdown_file
    except IOError as e:
        return False, f"Failed to write file {output_markdown_file}: {str(e)}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert knowledge base from JSONL format to Markdown format.")
    subparsers = parser.add_subparsers(dest='command', required=True)
    parser_kb = subparsers.add_parser('kb', help='Convert knowledge base file to Markdown.')
    parser_kb.add_argument("knowledge_base_file", help="Path to the knowledge base JSONL file.")
    parser_kb.add_argument("-o", "--output", default="knowledge_base.md", help="Output Markdown file name.")
    parser_vr = subparsers.add_parser('vr', help='Generate verification report from a directory.')
    parser_vr.add_argument("output_dir", help="Directory path containing verification_results.jsonl.")
    parser_vr.add_argument("-o", "--output", default="verification_report.md", help="Output Markdown file name for the verification report.")
    parser_vr.add_argument("-i", "--input", help="Input verification_results.jsonl file (default: output_dir/verification_results.jsonl).")
    args = parser.parse_args()

    if args.command == 'kb':
        success, message = convert_kb_to_markdown(args.knowledge_base_file, args.output)
        if success:
            print(f"Successfully converted knowledge base to {message}")
        else:
            print(f"Error: {message}")

    elif args.command == 'vr':
        results_file = args.input if hasattr(args, 'input') and args.input else None
        success, message = generate_verification_report_md(args.output_dir, args.output, results_file)
        if success:
            print(f"Successfully generated verification report: {message}")
        else:
            print(f"Error: {message}")