pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'  // The name you gave in Jenkins SonarQube config
    }

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${env.SONARQUBE_SERVER}") {
                    sh """
                        /opt/sonar-scanner/sonar-scanner-7.3.0.5189-linux-x64/bin/sonar-scanner \
                        -Dsonar.projectKey=ScanShield \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.token=squ_66b56e13a3ca9591c5f25832ac7135e5b5675326

                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                // Only works if the previous stage completed successfully
                waitForQualityGate abortPipeline: true
            }
        }

        stage('Build App') {
            steps {
                sh "docker compose build"
            }
        }

        stage('Deploy App') {
            steps {
                sh """
                docker compose down
                docker compose up -d --force-recreate
                """
            }
        }
    }
}
