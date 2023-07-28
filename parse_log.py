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

if __name__ == '__main__':
    logs = ["features.txt", "languagetool.txt", "ncs.txt", "restcountries.txt", "scs.txt", "genome.txt", "person.txt", "user.txt", "market.txt", "project.txt"]
    csvs = ["_11000_1.csv","_11010_1.csv","_11020_1.csv","_11030_1.csv","_11040_1.csv","_11050_1.csv","_11060_1.csv","_11070_1.csv","_11080_1.csv","_11090_1.csv"]
    result = [""]
    full_stack_traces = {}
    errors = {}

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
    for log_file in logs:
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

    with open("res.csv", "w") as f:
        f.write(result[0])

    with open('errors.json', 'w') as f:
        json.dump(errors, f)




