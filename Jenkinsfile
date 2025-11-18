pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'
        SONAR_TOKEN = 'squ_96754e8f46fcf62b692605612352ed6ca4e8bfb0'
        TRIVY_TIMEOUT = '5m'
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

        /* ====== FIRST APPROVAL ====== */
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

                        if (allowed.contains(approver)) {
                            echo "Approved by: ${approver}"
                            break
                        }
                        echo "'${approver}' is NOT allowed!"
                    }
                }
            }
        }

        /* ====== SECOND APPROVAL ====== */
        stage('Approval of operational team before build') {
            steps {
                script {
                    def allowed = ['dhananjay']
                    while (true) {
                        def approver = input(
                            message: "Approval required to proceed.\nOnly allowed: ${allowed}",
                            ok: "Approve",
                            submitterParameter: 'APPROVER'
                        )

                        if (allowed.contains(approver)) {
                            echo "Approved by: ${approver}"
                            break
                        }
                        echo "'${approver}' is NOT allowed!"
                    }
                }
            }
        }

        /* ====== SYFT SBOM SCAN ====== */
        stage('Syft SBOM Scan') {
            steps {
                sh """
                syft . -o json > syft-report.json
                syft . -o table > syft-report.txt
                """
            }
        }

        /* ====== TRIVY VULNERABILITY SCAN ====== */
stage('Trivy Vulnerability Scan (DOCX)') {
    steps {
        sh """
        export TRIVY_TIMEOUT=5m

        # 1️⃣ Generate report in Markdown (best for conversion)
        trivy fs . --scanners vuln \
            --db-repository public.ecr.aws/aquasecurity/trivy-db \
            -f markdown \
            -o trivy-report.md

        # 2️⃣ Convert Markdown → DOCX using pandoc
        pandoc trivy-report.md -o trivy-report.docx
        """
    }
}


        /* ====== BUILD ====== */
        stage('Build App') {
            steps {
                sh "docker compose build"
            }
        }

        /* ====== DEPLOY ====== */
        stage('Deploy App') {
            steps {
                sh """
                docker compose down
                docker compose up -d --force-recreate
                """
            }
        }
    }

    /* ====== ARCHIVE REPORTS IN JENKINS UI ====== */
    post {
        always {
            archiveArtifacts artifacts: '*.json, *.txt, trivy-report.docx', fingerprint: true

        }

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
