pipeline {
    agent any

    tools {
        sonarScanner 'SonarScanner'  // Name from Jenkins Global Tool Configuration
    }

    environment {
        SONARQUBE_SERVER = 'sonarqube'  // Name from Jenkins SonarQube configuration
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
                        sonar-scanner \
                        -Dsonar.projectKey=ScanShield \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.login=squ_66b56e13a3ca9591c5f25832ac7135e5b5675326
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                // This will abort the pipeline if the Quality Gate fails
                waitForQualityGate abortPipeline: true
            }
        }

        stage('Build App with Docker Compose') {
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
