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

        /* ============ SONAR SCAN ============ */
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

        /* ============ FIRST APPROVAL ============ */
        stage('Approval Before Build') {
            steps {
                script {
                    def allowed = ['admin', 'auditor']
                    while (true) {
                        def approver = input(
                            message: "Approval required. Allowed only: ${allowed}",
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

        /* ============ SECOND APPROVAL ============ */
        stage('Operational Team Approval') {
            steps {
                script {
                    def allowed = ['dhananjay']
                    while (true) {
                        def approver = input(
                            message: "Operational Approval required. Allowed only: ${allowed}",
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

        /* ============ SYFT SBOM SCAN ============ */
        stage('Syft SBOM Scan') {
            steps {
                sh """
                syft . -o json > syft-report.json
                syft . -o table > syft-report.txt
                """
            }
        }

        /* ============ TRIVY SCAN (HTML + DOCX) ============ */
        stage('Trivy Vulnerability Scan (HTML + DOCX)') {
            steps {
                sh """
                export TRIVY_TIMEOUT=5m

                # --- 1️⃣ Create HTML Template ---
                cat << 'EOF' > trivy-html.tpl
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<title>Trivy Vulnerability Report</title>
<style>
body { font-family: Arial; margin: 20px; }
table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
th, td { padding: 8px; border: 1px solid #ddd; }
th { background-color: #f2f2f2; }
.critical { background-color: #ffcccc; }
.high { background-color: #ffe0cc; }
.medium { background-color: #fff5cc; }
.low { background-color: #e6f7ff; }
</style>
</head>
<body>
<h1>Trivy Vulnerability Report</h1>
<p>Generated on: {{ .GeneratedAt }}</p>
{{ range .Results }}
<h2>Target: {{ .Target }}</h2>
<table>
<tr>
<th>Package</th>
<th>Installed</th>
<th>Fixed</th>
<th>CVE</th>
<th>Severity</th>
<th>Title</th>
</tr>
{{ range .Vulnerabilities }}
<tr class="{{ lower .Severity }}">
<td>{{ .PkgName }}</td>
<td>{{ .InstalledVersion }}</td>
<td>{{ .FixedVersion }}</td>
<td>{{ .VulnerabilityID }}</td>
<td>{{ .Severity }}</td>
<td>{{ .Title }}</td>
</tr>
{{ end }}
</table>
{{ end }}
</body>
</html>
EOF

                # --- 2️⃣ Generate HTML ---
                trivy fs . --scanners vuln \
                    --db-repository public.ecr.aws/aquasecurity/trivy-db \
                    --format template \
                    --template "@trivy-html.tpl" \
                    -o trivy-report.html

                # --- 3️⃣ Generate Markdown ---
                trivy fs . --scanners vuln \
                    --db-repository public.ecr.aws/aquasecurity/trivy-db \
                    -f template \
                    --template "@trivy-html.tpl" \
                    -o trivy-report.md

                # --- 4️⃣ Convert Markdown → DOCX ---
                pandoc trivy-report.md -o trivy-report.docx
                """
            }
        }

        /* ============ BUILD APP ============ */
        stage('Build App') {
            steps {
                sh "docker compose build"
            }
        }

        /* ============ DEPLOY APP ============ */
        stage('Deploy App') {
            steps {
                sh """
                docker compose down
                docker compose up -d --force-recreate
                """
            }
        }

        /* ============ PUBLISH HTML REPORT ============ */
        stage('Publish Vulnerability Report') {
            steps {
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'trivy-report.html',
                    reportName: 'Trivy Vulnerability Report'
                ])
            }
        }
    }

    /* ============ POST ACTIONS ============ */
    post {
        always {
            archiveArtifacts artifacts: '*.json, *.txt, *.md, *.html, *.docx', fingerprint: true
        }

        success {
            emailext(
                to: 'dhananjaykhairnar15@gmail.com',
                subject: "SUCCESS: Build #${env.BUILD_NUMBER}",
                body: """
                <p>Hi Team,</p>
                <p>The Jenkins build <b>#${env.BUILD_NUMBER}</b> completed successfully.</p>
                <p>Reports generated:<br>
                - SBOM (JSON + TXT)<br>
                - Trivy HTML Report<br>
                - Trivy DOCX Report
                </p>
                <p>Regards,<br>Jenkins</p>
                """,
                mimeType: 'text/html'
            )
        }
    }
}
