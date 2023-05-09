import subprocess
import time
import sys
import os

def run_service(service_path, class_name):
    with open(service_path + "/cp.txt", 'r') as f:
        cp = f.read()
    with open(service_path + "/run.sh", 'w') as f:
        f.write("java -Djdk.attach.allowAttachSelf=true " + cov + " -cp target/classes:target/test-classes:" + cp + ' ' + class_name)
    if name == "market" or name == "project-tracking-system":
        subprocess.run(". ./java11.env && cd " + service_path + " && tmux new-session -d -s " + name + " 'sudo sh run.sh'", shell=True)
    else:
        subprocess.run(". ./java8.env && cd " + service_path + " && tmux new-session -d -s " + name + " 'sudo sh run.sh'", shell=True)


if __name__ == "__main__":
    name = sys.argv[1]
    cov_port = sys.argv[2]
    evo = sys.argv[3]
    base = os.getcwd()

    cov1 = '-javaagent:' + base +'/org.jacoco.agent-0.8.7-runtime.jar=includes=*,output=tcpserver,port="'
    cov2 = '",address=*,dumponexit=true -Dfile.encoding=UTF-8'
    cov = cov1 + str(cov_port) + cov2

    if evo == "whitebox":
        if name == "features-service":
            run_service("./service/jdk8_1/em/embedded/rest/features-service", "em.embedded.org.javiermf.features.EmbeddedEvoMasterController")
            subprocess.run("tmux new -d -s features_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40101 -p 30101 -s proxy/features.py'", shell=True)
        elif name == "languagetool":
            run_service("./service/jdk8_1/em/embedded/rest/languagetool", "em.embedded.org.languagetool.EmbeddedEvoMasterController")
            subprocess.run(
                "tmux new -d -s language_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40100 -p 30100 -s proxy/languagetool.py'",
                shell=True)
        elif name == "ncs":
            run_service("./service/jdk8_1/em/embedded/rest/ncs", "em.embedded.org.restncs.EmbeddedEvoMasterController")
            subprocess.run(
                "tmux new -d -s ncs_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40102 -p 30102 -s proxy/ncs.py'",
                shell=True)
        elif name == "restcountries":
            run_service("./service/jdk8_1/em/embedded/rest/restcountries", "em.embedded.eu.fayder.EmbeddedEvoMasterController")
            subprocess.run(
                "tmux new -d -s restcountries_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40106 -p 30106 -s proxy/restcountries.py'",
                shell=True)
        elif name == "scs":
            run_service("./service/jdk8_1/em/embedded/rest/scs", "em.embedded.org.restscs.EmbeddedEvoMasterController")
            subprocess.run(
                "tmux new -d -s scs_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40108 -p 30108 -s proxy/scs.py'",
                shell=True)
        elif name == "genome-nexus":
            run_service("./service/jdk8_2/genome-nexus/web", "org.evo.EMDriver")
            subprocess.run(
                "tmux new -d -s genome_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40110 -p 30110 -s proxy/genome.py'",
                shell=True)
        elif name == "person-controller":
            run_service("./service/jdk8_2/person-controller", "org.evo.EMDriver")
            subprocess.run(
                "tmux new -d -s person_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40111 -p 30111 -s proxy/person.py'",
                shell=True)
        elif name == "user-management":
            run_service("./service/jdk8_2/user-management", "org.evo.EMDriver")
            subprocess.run(
                "tmux new -d -s user_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40116 -p 30116 -s proxy/user.py'",
                shell=True)
        elif name == "market":
            run_service("./service/jdk11/market/market-rest", "org.evo.EMDriver")
            subprocess.run(
                "tmux new -d -s market_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40118 -p 30118 -s proxy/market.py'",
                shell=True)
        elif name == "project-tracking-system":
            run_service("./service/jdk11/project-tracking-system", "org.evo.EMDriver")
            subprocess.run(
                "tmux new -d -s project_proxy 'mitmproxy --mode reverse:http://0.0.0.0:40119 -p 30119 -s proxy/project.py'",
                shell=True)
    else:
        if name == "features-service":
            run_service("./service/jdk8_1/em/embedded/rest/features-service", "em.embedded.org.javiermf.features.RunServer")
            subprocess.run(
                "tmux new -d -s features_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50100 -p 30100 -s proxy/features.py'",
                shell=True)
        elif name == "languagetool":
            run_service("./service/jdk8_1/em/embedded/rest/languagetool", "em.embedded.org.languagetool.RunServer")
            subprocess.run(
                "tmux new -d -s language_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50101 -p 30101 -s proxy/languagetool.py'",
                shell=True)
        elif name == "ncs":
            run_service("./service/jdk8_1/em/embedded/rest/ncs", "em.embedded.org.restncs.RunServer")
            subprocess.run(
                "tmux new -d -s ncs_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50102 -p 30102 -s proxy/ncs.py'",
                shell=True)
        elif name == "restcountries":
            run_service("./service/jdk8_1/em/embedded/rest/restcountries", "em.embedded.eu.fayder.RunServer")
            subprocess.run(
                "tmux new -d -s restcountries_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50106 -p 30106 -s proxy/restcountries.py'",
                shell=True)
        elif name == "scs":
            run_service("./service/jdk8_1/em/embedded/rest/scs", "em.embedded.org.restscs.RunServer")
            subprocess.run(
                "tmux new -d -s scs_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50108 -p 30108 -s proxy/scs.py'",
                shell=True)
        elif name == "genome-nexus":
            subprocess.run("sudo docker run --name=gn-mongo --restart=always -p 27018:27017 -d genomenexus/gn-mongo:latest", shell=True)
            time.sleep(30)
            subprocess.run("tmux new -d -s genome-nexus '. java8.env && java " + cov + " -jar ./service/jdk8_2/genome-nexus/web/target/web-0-unknown-version-SNAPSHOT.war'", shell=True)
            subprocess.run(
                "tmux new -d -s genome_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50110 -p 30110 -s proxy/genome.py'",
                shell=True)
        elif name == "person-controller":
            subprocess.run("sudo docker run -d -p 27019:27017 --name mongodb mongo:latest", shell=True)
            time.sleep(30)
            subprocess.run("tmux new -d -s person-controller '. java8.env && java " + cov + " -jar ./service/jdk8_2/person-controller/target/java-spring-boot-mongodb-starter-1.0.0.jar'", shell=True)
            subprocess.run(
                "tmux new -d -s person_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50111 -p 30111 -s proxy/person.py'",
                shell=True)
        elif name == "user-management":
            subprocess.run("sudo docker run -d -p 3306:3306 --name mysqldb -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=users mysql", shell=True)
            time.sleep(30)
            subprocess.run("tmux new -d -s user-management '. java8.env && java " + cov + " -jar ./service/jdk8_2/user-management/target/microdemo2-1.0.0-SNAPSHOT.jar'" , shell=True)
            subprocess.run(
                "tmux new -d -s user_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50115 -p 30115 -s proxy/user.py'",
                shell=True)
        elif name == "market":
            subprocess.run("tmux new -d -s market '. java11.env && java -Djdk.attach.allowAttachSelf=true " + cov + " -jar ./service/jdk11/market/market-rest/target/market-rest-0.1.2.jar'", shell=True)
            subprocess.run(
                "tmux new -d -s market_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50117 -p 30117 -s proxy/market.py'",
                shell=True)
        elif name == "project-tracking-system":
            subprocess.run("tmux new -d -s project-tracking-system '. java11.env && java -Djdk.attach.allowAttachSelf=true " + cov + " -jar ./service/jdk11/project-tracking-system/target/project-tracking-system.jar'", shell=True)
            subprocess.run(
                "tmux new -d -s project_proxy 'mitmproxy --mode reverse:http://0.0.0.0:50118 -p 30118 -s proxy/project.py'",
                shell=True)