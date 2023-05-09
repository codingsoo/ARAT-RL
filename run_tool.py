import os
import sys
import time
import subprocess


def whitebox(port):
    timeout = time.time() + 60 * 60 * int(time_limit)
    while time.time() < timeout:
        subprocess.run("rm -rf " + service, shell=True)
        subprocess.run("java -jar evomaster.jar --sutControllerPort " + str(port) + " --maxTime " + time_limit + "h --outputFolder " + service, shell=True)


def blackbox(swagger, port):
    timeout = time.time() + 60 * 60 * int(time_limit)
    while time.time() < timeout:
        if tool == "evomaster-blackbox":
            subprocess.run("rm -rf " + service, shell=True)
            subprocess.run("java -jar evomaster.jar --blackBox true --bbSwaggerUrl " + swagger + " --bbTargetUrl http://localhost:" + str(port) + " --outputFormat JAVA_JUNIT_4 --maxTime " + time_limit + "h --outputFolder " + service, shell=True)
        elif tool == "restler":
            basedir = os.path.join(curdir, "restler_" + service)
            restler_home = os.path.join(curdir, "restler/restler_bin/restler/Restler.dll")
            com1 = " && dotnet " + restler_home + " compile --api_spec " + swagger
            com2 = " && dotnet " + restler_home + " fuzz --grammar_file ./Compile/grammar.py --dictionary_file ./Compile/dict.json --settings ./Compile/engine_settings.json --no_ssl --time_budget " + time_limit
            subprocess.run("rm -rf " + basedir, shell=True)
            subprocess.run("mkdir " + basedir + " && cd " + basedir + com1 + com2, shell=True)
        elif tool == "morest":
            run = "cd morest && python fuzzer.py " + swagger
            options = " http://localhost:" + str(port)
            subprocess.run(run + options, shell=True)
        elif tool == "arat-rl":
            run = "python main.py " + swagger
            options = " http://localhost:" + str(port)
            subprocess.run(run + options, shell=True)
        elif tool == "no_prioritization":
            run = "python no_prioritization.py " + swagger
            options = " http://localhost:" + str(port)
            subprocess.run(run + options, shell=True)
        elif tool == "no_feedback":
            run = "python no_feedback.py " + swagger
            options = " http://localhost:" + str(port)
            subprocess.run(run + options, shell=True)
        elif tool == "no_sampling":
            run = "python no_sampling.py " + swagger
            options = " http://localhost:" + str(port)
            subprocess.run(run + options, shell=True)

if __name__ == "__main__":
    tool = sys.argv[1]
    service = sys.argv[2]
    port = sys.argv[3]
    time_limit = "1"

    curdir = os.getcwd()

    if tool == "evomaster-whitebox":
        subprocess.run("python3 run_service.py " + service + " " + str(port) + " whitebox", shell=True)
    else:
        subprocess.run("python3 run_service.py " + service + " " + str(port) + " blackbox", shell=True)

    print("Service started in the background. To check or kill the session, please see README file.")
    time.sleep(30)

    if service == "features-service":
        if tool == "evomaster-whitebox":
            whitebox(30101)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/features.yaml", 30100)
        else:
            blackbox(os.path.join(curdir, "spec/features.yaml"), 30100)
    elif service == "languagetool":
        if tool == "evomaster-whitebox":
            whitebox(30100)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/languagetool.yaml", 30101)
        else:
            blackbox(os.path.join(curdir, "spec/languagetool.yaml"), "30101/v2")
    elif service == "ncs":
        if tool == "evomaster-whitebox":
            whitebox(30102)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/ncs.yaml", 30102)
        else:
            blackbox(os.path.join(curdir, "spec/ncs.yaml"), 30102)
    elif service == "restcountries":
        if tool == "evomaster-whitebox":
            whitebox(30106)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/restcountries.yaml", "30106")
        else:
            blackbox(os.path.join(curdir, "spec/restcountries.yaml"), "30106/rest")
    elif service == "scs":
        if tool == "evomaster-whitebox":
            whitebox(30108)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/scs.yaml", 30108)
        else:
            blackbox(os.path.join(curdir, "spec/scs.yaml"), 30108)
    elif service == "genome-nexus":
        time.sleep(300)
        if tool == "evomaster-whitebox":
            whitebox(30110)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/genome.yaml", 30110)
        else:
            blackbox(os.path.join(curdir, "spec/genome.yaml"), 30110)
    elif service == "person-controller":
        if tool == "evomaster-whitebox":
            whitebox(30111)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/person.yaml", 30111)
        else:
            blackbox(os.path.join(curdir, "spec/person.yaml"), 30111)
    elif service == "user-management":
        if tool == "evomaster-whitebox":
            whitebox(30116)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/user.yaml", 30115)
        else:
            blackbox(os.path.join(curdir, "spec/user.yaml"), 30115)
    elif service == "market":
        if tool == "evomaster-whitebox":
            whitebox(30118)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/market.yaml", 30117)
        else:
            blackbox(os.path.join(curdir, "spec/market.yaml"), 30117)
    elif service == "project-tracking-system":
        if tool == "evomaster-whitebox":
            whitebox(30119)
        elif tool == "evomaster-blackbox":
            blackbox("file://$(pwd)/spec/project.yaml", 30118)
        else:
            blackbox(os.path.join(curdir, "spec/project.yaml"), 30118)

    print(
        "Experiments are done. We are safely closing the service now. If you want to run more, please check if there is unclosed session. You can check it with 'tmux ls' command. To close the session, you can run 'tmux kill-sess -t {session name}'")

    time.sleep(180)
    subprocess.run("tmux kill-sess -t " + service, shell=True)
