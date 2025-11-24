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

        /* ===== SONAR SCAN ===== */
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

        // /* ===== FIRST APPROVAL ===== */
        // stage('Approval Before Build') {
        //     steps {
        //         script {
        //             def allowed = ['admin', 'auditor']
        //             while (true) {
        //                 def approver = input(
        //                     message: "Approval required. Allowed only: ${allowed}",
        //                     ok: "Approve",
        //                     submitterParameter: 'APPROVER'
        //                 )
        //                 if (allowed.contains(approver)) {
        //                     echo "Approved by: ${approver}"
        //                     break
        //                 }
        //                 echo "'${approver}' is NOT allowed!"
        //             }
        //         }
        //     }
        // }

        // /* ===== SECOND APPROVAL ===== */
        // stage('Operational Team Approval') {
        //     steps {
        //         script {
        //             def allowed = ['dhananjay']
        //             while (true) {
        //                 def approver = input(
        //                     message: "Approval required. Allowed only: ${allowed}",
        //                     ok: "Approve",
        //                     submitterParameter: 'APPROVER'
        //                 )
        //                 if (allowed.contains(approver)) {
        //                     echo "Approved by: ${approver}"
        //                     break
        //                 }
        //                 echo "'${approver}' is NOT allowed!"
        //             }
        //         }
        //     }
        // }

        /* ===== SYFT SCAN ===== */
        stage('Syft SBOM Scan') {
            steps {
                sh """
                syft . -o json > syft-report.json
                syft . -o table > syft-report.txt
                """
            }
        }

        /* ===== TRIVY SCAN (HTML already exists) ===== */
stage('Trivy Vulnerability Scan') {
    steps {
        sh """
        echo "Creating Correct Trivy Template..."

cat << 'EOF' > trivy-report.tpl
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Trivy Vulnerability Report</title>
<style>
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background-color: #333; color: white; }
</style>
</head>

<body>
<h1>Trivy Vulnerability Report</h1>

{{- range .Results }}
<h2>Target: {{ .Target }}</h2>

{{- if .Vulnerabilities }}
<table>
    <tr>
        <th>Package</th>
        <th>Installed</th>
        <th>Vulnerability</th>
        <th>Severity</th>
        <th>Fixed Version</th>
        <th>Description</th>
    </tr>

    {{- range .Vulnerabilities }}
    <tr>
        <td>{{ .PkgName }}</td>
        <td>{{ .InstalledVersion }}</td>
        <td>{{ .VulnerabilityID }}</td>
        <td>{{ .Severity }}</td>
        <td>{{ .FixedVersion }}</td>
        <td>{{ .Description }}</td>
    </tr>
    {{- end }}
</table>
{{- else }}
<p>No vulnerabilities found.</p>
{{- end }}

{{- end }}

</body>
</html>
EOF

echo "Running Trivy Scan..."

trivy fs . --scanners vuln \
    --db-repository public.ecr.aws/aquasecurity/trivy-db \
    --format template \
    --template trivy-report.tpl \
    -o trivy-report.html

echo "Trivy Scan Completed."
        """
    }
}

        /* ===== BUILD ===== */
        stage('Build App') {
            steps {
                sh "docker compose build"
            }
        }

        /* ===== DEPLOY ===== */
        stage('Deploy App') {
            steps {
                sh """
                docker compose down
                docker compose up -d --force-recreate
                """
            }
        }

        /* ===== PUBLISH HTML REPORT ===== */
stage('Publish Vulnerability Report') {
    steps {
        publishHTML([
            reportDir: '.',
            reportFiles: 'trivy-report.html',
            reportName: 'Trivy Vulnerability Report',
            keepAll: true,
            alwaysLinkToLastBuild: true,
            allowMissing: false
        ])
    }
}

stage('OWASP ZAP DAST Scan') {
    steps {
        sh """
        echo "Starting OWASP ZAP Baseline Scan..."

        docker run --rm \
            -v $(pwd):/zap/wrk \
            -t owasp/zap2docker-stable zap-baseline.py \
            -t http://localhost:8000 \
            -r zap-report.html \
            -x zap-report.xml \
            -J zap-json-report.json \
            -I
        """
    }
}

    }

    /* ===== POST ACTIONS ===== */
    post {
        always {
            archiveArtifacts artifacts: '*.json, *.txt, *.html', fingerprint: true
        }

        success {
            emailext(
                to: 'dhananjaykhairnar15@gmail.com',
                subject: "SUCCESS: Build #${env.BUILD_NUMBER}",
                body: """
                <p>Hi Team,</p>
                <p>The Jenkins build <b>#${env.BUILD_NUMBER}</b> completed successfully.</p>
                <p>Vulnerability Report has been generated.</p>
                <p>Regards,<br>Jenkins</p>
                """,
                mimeType: 'text/html'
            )
        }
    }
}
