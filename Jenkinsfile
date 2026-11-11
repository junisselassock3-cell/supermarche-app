// Pipeline Jenkins : tests puis build + push de l'image sur Docker Hub
// Identifiants à créer dans Jenkins : type "Username with password",
// ID = dockerhub, username = lassock, password = jeton Docker Hub

pipeline {
    agent any
    options {
        disableConcurrentBuilds()
    }

    environment {
        IMAGE = 'lassock/supermarche-app'
    }

    stages {
        stage('Tests') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --default-timeout=120 --retries 10 --resume-retries 10 -r requirements-dev.txt
                    pytest -v
                '''
            }
        }

        stage('Build et push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub',
                                                  usernameVariable: 'DOCKER_USER',
                                                  passwordVariable: 'DOCKER_TOKEN')]) {
                    retry(3) {
                        sh '''
                            echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin
                            docker build -t "$IMAGE:latest" -t "$IMAGE:$GIT_COMMIT" .
                            docker push "$IMAGE:latest"
                            docker push "$IMAGE:$GIT_COMMIT"
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
    }
}
