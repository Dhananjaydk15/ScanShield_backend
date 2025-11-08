pipeline {
    agent any

    environment {
        APP_NAME = "fastapi-app"
        REGISTRY = "fastapi-app"   // change if using DockerHub later
    }

    stages {

        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        stage('Get Version Tag') {
            steps {
                script {
                    // use short commit hash as image tag
                    COMMIT_HASH = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    IMAGE_TAG = "${APP_NAME}:${COMMIT_HASH}"
                    echo "Building image: ${IMAGE_TAG}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build(IMAGE_TAG)
                }
            }
        }

        stage('Stop & Remove Old Container') {
            steps {
                sh """
                docker stop ${APP_NAME} || true
                docker rm ${APP_NAME} || true
                """
            }
        }

stage('Run New Container') {
    steps {
        script {
            sh """
            # Free port 8000 if in use
            container_id=\$(docker ps -q --filter "publish=8000")
            if [ ! -z "\$container_id" ]; then
                echo "Port 8000 is in use by container \$container_id. Stopping..."
                docker stop \$container_id
                docker rm \$container_id
            fi

            docker run -d --name ${APP_NAME} -p 8000:8000 ${IMAGE_TAG}
            """
        }
    }
}

    }
}
