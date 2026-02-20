#!/usr/bin/env python3
"""
ARAT-RL Setup Verification Script

This script verifies that all components of ARAT-RL are properly installed and configured.
"""

import subprocess
import os
import sys
import logging
from pathlib import Path

from logger_config import setup_logging

logger = logging.getLogger('verify-setup')

def run_command(cmd, description):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info('%s', description)
            return True
        else:
            logger.error('%s: %s', description, result.stderr.strip())
            return False
    except Exception as e:
        logger.error('%s: %s', description, str(e))
        return False

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        logger.info('%s', description)
        return True
    else:
        logger.error('%s: File not found', description)
        return False

def main():
    setup_logging('verify-setup')
    logger.info('ARAT-RL Setup Verification')
    logger.info('=' * 40)
    
    all_checks_passed = True
    
    # Check basic tools
    logger.info('')
    logger.info('1. Basic Tools:')
    all_checks_passed &= run_command("java -version", "Java is installed")
    all_checks_passed &= run_command("mvn -version", "Maven is installed")
    all_checks_passed &= run_command("docker --version", "Docker is installed")
    all_checks_passed &= run_command("python3 --version", "Python 3 is installed")
    all_checks_passed &= run_command("tmux -V", "tmux is installed")
    
    # Check Java versions
    logger.info('')
    logger.info('2. Java Versions:')
    java_output = subprocess.run("java -version", shell=True, capture_output=True, text=True)
    if "1.8" in java_output.stderr:
        logger.info('Java 8 detected')
    elif "11" in java_output.stderr:
        logger.info('Java 11 detected')
    else:
        logger.error('Unexpected Java version')
        all_checks_passed = False
    
    # Check environment files
    logger.info('')
    logger.info('3. Environment Files:')
    all_checks_passed &= check_file_exists("java8.env", "java8.env exists")
    all_checks_passed &= check_file_exists("java11.env", "java11.env exists")
    
    # Check build artifacts
    logger.info('')
    logger.info('4. Build Artifacts:')
    cp_files = list(Path("service").rglob("cp.txt"))
    if len(cp_files) == 6:
        logger.info('All %d cp.txt files found', len(cp_files))
    else:
        logger.error('Expected 6 cp.txt files, found %d', len(cp_files))
        all_checks_passed = False
    
    # Check JAR files
    logger.info('')
    logger.info('5. JAR Files:')
    all_checks_passed &= check_file_exists("evomaster.jar", "EvoMaster JAR")
    all_checks_passed &= check_file_exists("org.jacoco.agent-0.8.7-runtime.jar", "JaCoCo Agent JAR")
    all_checks_passed &= check_file_exists("org.jacoco.cli-0.8.7-nodeps.jar", "JaCoCo CLI JAR")
    
    # Check Python dependencies
    logger.info('')
    logger.info('6. Python Dependencies:')
    try:
        import yaml
        import requests
        logger.info('Required Python packages installed')
    except ImportError as e:
        logger.error('Missing Python package: %s', e)
        all_checks_passed = False
    
    # Check Docker images
    logger.info('')
    logger.info('7. Docker Images:')
    docker_images = subprocess.run("docker images", shell=True, capture_output=True, text=True)
    if "genomenexus/gn-mongo" in docker_images.stdout:
        logger.info('Genome Nexus MongoDB image')
    else:
        logger.error('Genome Nexus MongoDB image not found')
        all_checks_passed = False
    
    if "mongo" in docker_images.stdout:
        logger.info('MongoDB image')
    else:
        logger.error('MongoDB image not found')
        all_checks_passed = False
    
    if "mysql" in docker_images.stdout:
        logger.info('MySQL image')
    else:
        logger.error('MySQL image not found')
        all_checks_passed = False
    
    # Summary
    logger.info('')
    logger.info('=' * 40)
    if all_checks_passed:
        logger.info('All checks passed! ARAT-RL setup appears to be correct.')
        logger.info('')
        logger.info('You can now run:')
        logger.info('  python3 arat-rl.py spec/features.yaml http://localhost:30100/ 60')
    else:
        logger.error('Some checks failed. Please review the issues above.')
        logger.info('')
        logger.info('Common solutions:')
        logger.info('  - Run setup script: sh setup_macos.sh (macOS) or sh setup.sh (Ubuntu)')
        logger.info('  - Check troubleshooting guide: TROUBLESHOOTING.md')
        logger.info('  - Verify all dependencies are installed')
        sys.exit(1)

if __name__ == "__main__":
    main()
