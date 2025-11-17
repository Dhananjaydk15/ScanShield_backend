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

        /*** 🔥 Stage 1: Approval & Audit Logging ***/
        stage('Approval Before Build') {
            steps {
                script {
                    def allowed = ['admin', 'auditor']
                    def auditLog = "approval_audit_stage1.log"

                    writeFile file: auditLog, text: "=== Approval Audit Log: Stage 1 ===\n"

                    while (true) {
                        def approver = input(
                          message: "Approval required.\nOnly allowed: ${allowed}",
                          ok: "Approve",
                          submitterParameter: 'APPROVER'
                        )

                        echo "Stage 1: Attempt by: ${approver}"
                        writeFile file: auditLog, text: "Attempt by: ${approver} at ${new Date()}\n", append: true

                        if (allowed.contains(approver)) {
                            echo "Stage 1: APPROVED by ${approver}"
                            writeFile file: auditLog, text: "FINAL APPROVAL by: ${approver} at ${new Date()}\n", append: true
                            break
                        } else {
                            echo "⛔ '${approver}' is NOT allowed. Waiting..."
                        }
                    }

                    echo "Audit log saved: ${auditLog}"
                }
            }
        }

        /*** 🔥 Stage 2: OPS Team Approval & Logging ***/
        stage('Approval of operational team before build') {
            steps {
                script {
                    def allowed = ['dhananjay']
                    def auditLog = "approval_audit_stage2.log"

                    writeFile file: auditLog, text: "=== Approval Audit Log: Stage 2 ===\n"

                    while (true) {
                        def approver = input(
                          message: "Approval required.\nOnly allowed: ${allowed}",
                          ok: "Approve",
                          submitterParameter: 'APPROVER'
                        )

                        echo "Stage 2: Attempt by: ${approver}"
                        writeFile file: auditLog, text: "Attempt by: ${approver} at ${new Date()}\n", append: true

                        if (allowed.contains(approver)) {
                            echo "Stage 2: APPROVED by ${approver}"
                            writeFile file: auditLog, text: "FINAL APPROVAL by: ${approver} at ${new Date()}\n", append: true
                            break
                        } else {
                            echo "⛔ '${approver}' is NOT allowed. Waiting..."
                        }
                    }

                    echo "Audit log saved: ${auditLog}"
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
