pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def appName = "fastapi-app"
                    def dockerImage = docker.build("${appName}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                sh '''
                docker stop fastapi-container || true
                docker rm fastapi-container || true
                '''
            }
        }

        stage('Run New Container') {
            steps {
                sh '''
docker compose down
docker compose up --build -d

                '''
            }
        }
    }
}
