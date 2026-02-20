import os
import re
import json
import subprocess
from collections import Counter
from json import JSONDecodeError


def count_coverage(path, port):
    class_files = []
    jacoco_command2 = ''
    subdirs = [x[0] for x in os.walk(path)]
    for subdir in subdirs:
        if '/target/classes/' in subdir:
            target_dir = subdir[:subdir.rfind('/target/classes/') + 15]
            if target_dir not in class_files:
                class_files.append(target_dir)
                jacoco_command2 = jacoco_command2 + ' --classfiles ' + target_dir
        if '/build/classes/' in subdir:
            target_dir = subdir[:subdir.rfind('/build/classes/') + 14]
            if target_dir not in class_files:
                class_files.append(target_dir)
                jacoco_command2 = jacoco_command2 + ' --classfiles ' + target_dir

    jacoco_command2 = jacoco_command2 + ' --csv '
    jacoco_command1 = 'java -jar org.jacoco.cli-0.8.7-nodeps.jar report '
    jacoco_file = port + '.csv'
    subprocess.run(jacoco_command1 + "jacoco" + port + ".exec" + jacoco_command2 + jacoco_file, shell=True)

def parse_log_file(file_path):
    log_data = []
    status2xx = 0
    status4xx = 0
    status5xx = 0
    with open(file_path, 'r') as f:
        current_log = {}
        for line in f:
            if "========REQUEST========" in line:
                current_log = {'request': {}, 'response': {}}
            elif "========RESPONSE========" in line:
                if "response" in current_log:
                    current_log['response']['timestamp'] = float(f.readline().strip())
                    current_log['response']['status_code'] = int(f.readline().strip())
                    status = current_log['response']['status_code'] // 100
                    if status == 2:
                        status2xx += 1
                    elif status == 4:
                        status4xx += 1
                    elif status == 5:
                        status5xx += 1
            elif current_log:
                if 'text' not in current_log['response']:
                    current_log['response']['text'] = ''
                current_log['response']['text'] += line
                if "</html>" in line:
                    log_data.append(current_log)
                    current_log = {}
                if "Error" in line:
                    log_data.append(current_log)
                    current_log = {}
    result[0] = result[0] + str(status2xx + status4xx + status5xx) + ',' + str(status2xx)+ ',' + str(status4xx) + ',' + str(status5xx) + ','
    print("Total: " + str(status2xx + status4xx + status5xx))
    print("Status 2xx: " + str(status2xx))
    print("Status 4xx: " + str(status4xx))
    print("Status 5xx: " + str(status5xx))


    return log_data

def count_unique_5xx_errors(log_data):
    unique_stack_traces = Counter()

    for log_item in log_data:
        if 'response' in log_item and "status_code" in log_item['response']:
            status_code = log_item['response']['status_code']
            response_text = log_item['response']['text']

            if status_code // 100 == 5:

                if "stackTrace" in response_text:
                    response_text = response_text[response_text.find('"stackTrace"'):]
                    response_text = response_text[:response_text.find('java.lang.Thread')]
                    response_text = response_text[:response_text.find('Thread.java')]
                elif "<title>" in response_text:
                    response_text = response_text[response_text.find("<title>"):response_text.find("</title>")]
                elif "java:" in response_text:
                    response_text = re.findall(r"\w+\.java:\d+", response_text)
                    response_text = ', '.join(response_text)
                else:
                    response_text = response_text[response_text.find("Error:"):]
                    response_text = re.sub(r'\[.*?\]', '', response_text)  # Remove words in square brackets
                    response_text = re.sub(r'\(.*?\)', '', response_text)  # Remove words in round brackets
                    response_text = re.sub(r'\'(.*?)\'|"(\1)"', '', response_text)  # Remove words in single or double quotes

                error_message = response_text.strip()
                unique_stack_traces[error_message] += 1
                full_stack_traces[error_message] = log_item['response']['text']

    return unique_stack_traces


def generate_html_report(services_data, errors):
    import html as html_module

    total_requests = sum(s['total'] for s in services_data)
    total_errors = sum(s['status_5xx'] for s in services_data)
    total_unique_5xx = sum(s['unique_5xx'] for s in services_data)
    num_services = len(services_data) if services_data else 1
    avg_branch = sum(s['branch_cov'] for s in services_data) / num_services
    avg_line = sum(s['line_cov'] for s in services_data) / num_services
    avg_method = sum(s['method_cov'] for s in services_data) / num_services

    def cov_color(val):
        if val < 50:
            return '#e74c3c'
        elif val < 80:
            return '#f39c12'
        else:
            return '#27ae60'

    summary_cards = '''
    <div class="cards">
      <div class="card">
        <div class="card-value">{total_requests}</div>
        <div class="card-label">Total Requests</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:#e74c3c">{total_errors}</div>
        <div class="card-label">5xx Errors</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:#f39c12">{total_unique_5xx}</div>
        <div class="card-label">Unique 5xx Faults</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:{branch_color}">{avg_branch:.1f}%</div>
        <div class="card-label">Avg Branch Coverage</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:{line_color}">{avg_line:.1f}%</div>
        <div class="card-label">Avg Line Coverage</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:{method_color}">{avg_method:.1f}%</div>
        <div class="card-label">Avg Method Coverage</div>
      </div>
    </div>
    '''.format(
        total_requests=total_requests,
        total_errors=total_errors,
        total_unique_5xx=total_unique_5xx,
        avg_branch=avg_branch,
        avg_line=avg_line,
        avg_method=avg_method,
        branch_color=cov_color(avg_branch),
        line_color=cov_color(avg_line),
        method_color=cov_color(avg_method),
    )

    # Status code distribution bars
    status_rows = ''
    for s in services_data:
        total = s['total'] if s['total'] > 0 else 1
        pct_2xx = s['status_2xx'] / total * 100
        pct_4xx = s['status_4xx'] / total * 100
        pct_5xx = s['status_5xx'] / total * 100
        status_rows += '''
        <div class="status-row">
          <div class="status-label">{name}</div>
          <div class="status-bar-container">
            <div class="status-bar bar-2xx" style="width:{pct_2xx:.1f}%" title="2xx: {count_2xx} ({pct_2xx:.1f}%)"></div>
            <div class="status-bar bar-4xx" style="width:{pct_4xx:.1f}%" title="4xx: {count_4xx} ({pct_4xx:.1f}%)"></div>
            <div class="status-bar bar-5xx" style="width:{pct_5xx:.1f}%" title="5xx: {count_5xx} ({pct_5xx:.1f}%)"></div>
          </div>
          <div class="status-counts">{total} total</div>
        </div>
        '''.format(
            name=html_module.escape(s['name']),
            pct_2xx=pct_2xx, pct_4xx=pct_4xx, pct_5xx=pct_5xx,
            count_2xx=s['status_2xx'], count_4xx=s['status_4xx'], count_5xx=s['status_5xx'],
            total=s['total'],
        )

    # Coverage dashboard
    coverage_rows = ''
    for s in services_data:
        coverage_rows += '''
        <div class="cov-service">
          <div class="cov-service-name">{name}</div>
          <div class="cov-bars">
            <div class="cov-row">
              <span class="cov-type">Branch</span>
              <div class="cov-bar-bg">
                <div class="cov-bar-fill" style="width:{branch:.1f}%;background:{branch_c}"></div>
              </div>
              <span class="cov-pct">{branch:.1f}%</span>
            </div>
            <div class="cov-row">
              <span class="cov-type">Line</span>
              <div class="cov-bar-bg">
                <div class="cov-bar-fill" style="width:{line:.1f}%;background:{line_c}"></div>
              </div>
              <span class="cov-pct">{line:.1f}%</span>
            </div>
            <div class="cov-row">
              <span class="cov-type">Method</span>
              <div class="cov-bar-bg">
                <div class="cov-bar-fill" style="width:{method:.1f}%;background:{method_c}"></div>
              </div>
              <span class="cov-pct">{method:.1f}%</span>
            </div>
          </div>
        </div>
        '''.format(
            name=html_module.escape(s['name']),
            branch=s['branch_cov'], line=s['line_cov'], method=s['method_cov'],
            branch_c=cov_color(s['branch_cov']),
            line_c=cov_color(s['line_cov']),
            method_c=cov_color(s['method_cov']),
        )

    # Error details
    error_sections = ''
    for s in services_data:
        sname = s['name']
        service_errors = errors.get(sname, [])
        if not service_errors:
            continue
        traces_html = ''
        for idx, trace in enumerate(service_errors):
            traces_html += '<pre class="stack-trace">{trace}</pre>\n'.format(
                trace=html_module.escape(str(trace))
            )
        error_sections += '''
        <div class="error-service">
          <div class="error-header" onclick="toggleErrors(this)">
            <span class="error-toggle">&#9654;</span>
            <span class="error-sname">{name}</span>
            <span class="error-count">{count} unique error(s)</span>
          </div>
          <div class="error-body" style="display:none">
            {traces}
          </div>
        </div>
        '''.format(
            name=html_module.escape(sname),
            count=len(service_errors),
            traces=traces_html,
        )

    if not error_sections:
        error_sections = '<p class="no-errors">No 5xx errors found.</p>'

    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ARAT-RL Test Report</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background:#f0f2f5; color:#333; line-height:1.6; }}
.hero {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color:#fff; padding:40px 0; text-align:center; }}
.hero h1 {{ font-size:2.2em; font-weight:700; margin-bottom:8px; }}
.hero p {{ font-size:1.1em; opacity:0.85; }}
.container {{ max-width:1200px; margin:0 auto; padding:20px; }}
.section {{ background:#fff; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,0.08); margin-bottom:24px; padding:28px; }}
.section h2 {{ font-size:1.4em; color:#1a1a2e; margin-bottom:20px; padding-bottom:12px; border-bottom:2px solid #e8e8e8; }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:16px; }}
.card {{ background:#fff; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06); padding:24px 16px; text-align:center; border:1px solid #eee; }}
.card-value {{ font-size:1.8em; font-weight:700; margin-bottom:4px; }}
.card-label {{ font-size:0.9em; color:#666; text-transform:uppercase; letter-spacing:0.5px; }}
.status-row {{ display:flex; align-items:center; margin-bottom:12px; gap:12px; }}
.status-label {{ width:160px; font-weight:600; font-size:0.9em; flex-shrink:0; text-align:right; }}
.status-bar-container {{ flex:1; height:28px; background:#eee; border-radius:6px; overflow:hidden; display:flex; }}
.status-bar {{ height:100%; transition:width 0.3s; }}
.bar-2xx {{ background:#27ae60; }}
.bar-4xx {{ background:#f39c12; }}
.bar-5xx {{ background:#e74c3c; }}
.status-counts {{ width:100px; font-size:0.85em; color:#666; flex-shrink:0; }}
.legend {{ display:flex; gap:20px; margin-bottom:16px; font-size:0.9em; }}
.legend-item {{ display:flex; align-items:center; gap:6px; }}
.legend-dot {{ width:14px; height:14px; border-radius:3px; }}
.cov-service {{ margin-bottom:20px; padding-bottom:16px; border-bottom:1px solid #f0f0f0; }}
.cov-service:last-child {{ border-bottom:none; margin-bottom:0; padding-bottom:0; }}
.cov-service-name {{ font-weight:600; font-size:1.05em; margin-bottom:8px; }}
.cov-bars {{ display:flex; flex-direction:column; gap:6px; }}
.cov-row {{ display:flex; align-items:center; gap:10px; }}
.cov-type {{ width:65px; font-size:0.85em; color:#666; flex-shrink:0; }}
.cov-bar-bg {{ flex:1; height:20px; background:#eee; border-radius:4px; overflow:hidden; }}
.cov-bar-fill {{ height:100%; border-radius:4px; transition:width 0.3s; }}
.cov-pct {{ width:55px; font-size:0.85em; font-weight:600; text-align:right; flex-shrink:0; }}
.error-service {{ margin-bottom:12px; border:1px solid #eee; border-radius:8px; overflow:hidden; }}
.error-header {{ padding:14px 18px; background:#fafafa; cursor:pointer; display:flex; align-items:center; gap:10px; user-select:none; }}
.error-header:hover {{ background:#f0f0f0; }}
.error-toggle {{ font-size:0.8em; transition:transform 0.2s; display:inline-block; }}
.error-toggle.open {{ transform:rotate(90deg); }}
.error-sname {{ font-weight:600; flex:1; }}
.error-count {{ font-size:0.85em; color:#e74c3c; background:#fde8e8; padding:2px 10px; border-radius:12px; }}
.error-body {{ padding:16px; background:#fff; }}
.stack-trace {{ background:#1e1e2e; color:#cdd6f4; padding:16px; border-radius:6px; font-size:0.82em; overflow-x:auto; margin-bottom:10px; white-space:pre-wrap; word-wrap:break-word; line-height:1.5; }}
.stack-trace:last-child {{ margin-bottom:0; }}
.no-errors {{ color:#27ae60; font-style:italic; }}
footer {{ text-align:center; padding:20px; color:#999; font-size:0.85em; }}
@media (max-width:768px) {{
  .status-label {{ width:100px; font-size:0.8em; }}
  .status-counts {{ width:70px; }}
  .cards {{ grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); }}
}}
</style>
</head>
<body>
<div class="hero">
  <h1>ARAT-RL Test Report</h1>
  <p>REST API Testing Results &mdash; Coverage &amp; Error Analysis</p>
</div>
<div class="container">
  <div class="section">
    <h2>Executive Summary</h2>
    {summary_cards}
  </div>
  <div class="section">
    <h2>Status Code Distribution</h2>
    <div class="legend">
      <div class="legend-item"><div class="legend-dot" style="background:#27ae60"></div> 2xx Success</div>
      <div class="legend-item"><div class="legend-dot" style="background:#f39c12"></div> 4xx Client Error</div>
      <div class="legend-item"><div class="legend-dot" style="background:#e74c3c"></div> 5xx Server Error</div>
    </div>
    {status_rows}
  </div>
  <div class="section">
    <h2>Code Coverage Dashboard</h2>
    {coverage_rows}
  </div>
  <div class="section">
    <h2>Error Details</h2>
    {error_sections}
  </div>
</div>
<footer>Generated by ARAT-RL parse_log.py</footer>
<script>
function toggleErrors(el) {{
  var body = el.nextElementSibling;
  var toggle = el.querySelector('.error-toggle');
  if (body.style.display === 'none') {{
    body.style.display = 'block';
    toggle.classList.add('open');
  }} else {{
    body.style.display = 'none';
    toggle.classList.remove('open');
  }}
}}
</script>
</body>
</html>'''.format(
        summary_cards=summary_cards,
        status_rows=status_rows,
        coverage_rows=coverage_rows,
        error_sections=error_sections,
    )

    with open('report.html', 'w') as f:
        f.write(html_content)


if __name__ == '__main__':
    logs = ["features.txt", "languagetool.txt", "ncs.txt", "restcountries.txt", "scs.txt", "genome.txt", "person.txt", "user.txt", "market.txt", "project.txt"]
    service_names = ["Features", "LanguageTool", "NCS", "REST Countries", "SCS", "Genome Nexus", "Person Controller", "User Management", "Market Service", "Project Tracking"]
    csvs = ["_11000_1.csv","_11010_1.csv","_11020_1.csv","_11030_1.csv","_11040_1.csv","_11050_1.csv","_11060_1.csv","_11070_1.csv","_11080_1.csv","_11090_1.csv"]
    result = [""]
    full_stack_traces = {}
    errors = {}
    services_data = []

    count_coverage("service/jdk8_1/cs/rest/original/features-service", "_11000_1")
    count_coverage("service/jdk8_1/cs/rest/original/languagetool/", "_11010_1")
    count_coverage("service/jdk8_1/cs/rest/artificial/ncs/", "_11020_1")
    count_coverage("service/jdk8_1/cs/rest/original/restcountries/", "_11030_1")
    count_coverage("service/jdk8_1/cs/rest/artificial/scs/", "_11040_1")
    count_coverage("service/jdk8_2/genome-nexus/", "_11050_1")
    count_coverage("service/jdk8_2/person-controller/", "_11060_1")
    count_coverage("service/jdk8_2/user-management", "_11070_1")
    count_coverage("service/jdk11/market", "_11080_1")
    count_coverage("service/jdk11/project-tracking-system", "_11090_1")
    for idx, log_file in enumerate(logs):
        print(log_file)
        errors[log_file] = []
        log_data = parse_log_file(log_file)
        unique_stack_traces = count_unique_5xx_errors(log_data)
        unique_5xx_count = 0
        for stack_trace, count in unique_stack_traces.items():
            errors[log_file].append(full_stack_traces[stack_trace])
            unique_5xx_count += 1
        print(f'\nTotal unique number of 5xx errors: {unique_5xx_count}')
        result[0] = result[0] + str(unique_5xx_count) + '\n'
        services_data.append({
            'name': service_names[idx],
            'log_file': log_file,
            'total': 0,
            'status_2xx': 0,
            'status_4xx': 0,
            'status_5xx': 0,
            'unique_5xx': unique_5xx_count,
            'branch_cov': 0.0,
            'line_cov': 0.0,
            'method_cov': 0.0,
        })

    # Parse the result string to extract status counts for each service
    result_lines = result[0].strip().split('\n')
    for idx, line in enumerate(result_lines):
        parts = line.split(',')
        if len(parts) >= 4:
            services_data[idx]['total'] = int(parts[0])
            services_data[idx]['status_2xx'] = int(parts[1])
            services_data[idx]['status_4xx'] = int(parts[2])
            services_data[idx]['status_5xx'] = int(parts[3])

    for i in range(10):
        total_branch = 0
        covered_branch = 0
        total_line = 0
        covered_line = 0
        total_method = 0
        covered_method = 0
        with open(csvs[i]) as f:
            lines = f.readlines()
            for line in lines:
                items = line.split(",")
                if '_COVERED' not in items[6] and '_MISSED' not in items[6]:
                    covered_branch = covered_branch + int(items[6])
                    total_branch = total_branch + int(items[6]) + int(items[5])
                    covered_line = covered_line + int(items[8])
                    total_line = total_line + int(items[8]) + int(items[7])
                    covered_method = covered_method + int(items[12])
                    total_method = total_method + int(items[12]) + int(items[11])
        print(covered_branch/total_branch*100, covered_line/total_line*100, covered_method/total_method*100)
        result[0] = result[0] + str(covered_method/total_method*100) + ',' + str(covered_branch/total_branch*100) + ',' + str(covered_line/total_line*100) + '\n'
        services_data[i]['branch_cov'] = covered_branch / total_branch * 100
        services_data[i]['line_cov'] = covered_line / total_line * 100
        services_data[i]['method_cov'] = covered_method / total_method * 100

    with open("res.csv", "w") as f:
        f.write(result[0])

    with open('errors.json', 'w') as f:
        json.dump(errors, f)

    # Build errors dict keyed by service name for HTML report
    errors_by_name = {}
    for idx, log_file in enumerate(logs):
        errors_by_name[service_names[idx]] = errors.get(log_file, [])

    generate_html_report(services_data, errors_by_name)




