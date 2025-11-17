pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'
        SONAR_TOKEN = 'squ_96754e8f46fcf62b692605612352ed6ca4e8bfb0'
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
                        -Dsonar.token=$SONAR_TOKEN
                    """
                }
            }
        }

stage('Approval Before Build') {
  steps {
    script {
      def allowed = ['admin', 'auditor']

      while (true) {
        def approver = input(
          message: "Approval required to proceed.\nOnly allowed: ${allowed}",
          ok: "Approve",
          submitterParameter: 'APPROVER'
        )

        echo "Attempted approval by: ${approver}"

        if (allowed.contains(approver)) {
          echo "Approved by allowed user: ${approver}"
          break   // exit loop and continue pipeline
        } else {
          echo " '${approver}' is NOT allowed. Waiting for correct user..."
          // loop continues → waits again
        }
      }
    }
  }
}

        /*** 🔥 Add Manual Approval Here ***/
stage('Approval of oprational team before build') {
  steps {
    script {
      def allowed = ['dhananjay']

      while (true) {
        def approver = input(
          message: "Approval required to proceed.\nOnly allowed: ${allowed}",
          ok: "Approve",
          submitterParameter: 'APPROVER'
        )

        echo "Attempted approval by: ${approver}"

        if (allowed.contains(approver)) {
          echo "Approved by allowed user: ${approver}"
          break   // exit loop and continue pipeline
        } else {
          echo "'${approver}' is NOT allowed. Waiting for correct user..."
          // loop continues → waits again
        }
      }
    }
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

    post {
        success {
            emailext(
                to: 'dhananjaykhairnar15@gmail.com',
                subject: "SUCCESS: Build #${env.BUILD_NUMBER}",
                body: """<p>Hi Team,</p>
                         <p>The Jenkins build <b>#${env.BUILD_NUMBER}</b> completed successfully.</p>
                         <p>Regards,<br>Jenkins</p>""",
                mimeType: 'text/html'
            )
        }
    }
}
