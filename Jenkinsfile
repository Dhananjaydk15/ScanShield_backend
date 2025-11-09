pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'  
    }

    stages {

        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
withSonarQubeEnv('sonarqube') {
    sh 'SonarScanner'
}
            }
        }

        stage('Quality Gate') {
            steps {
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
