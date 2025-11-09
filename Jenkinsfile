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
    sh "/opt/sonar-scanner/sonar-scanner-7.3.0.5189-linux-x64/bin/sonar-scanner -Dsonar.projectKey=ScanShield -Dsonar.sources=."
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
