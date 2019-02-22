pipeline {
  agent any

  environment {
    // Necessary so that `docker login` credentials are not put in shared location
    HOME = "${env.WORKSPACE}"
    DOCKER_REGISTRY = 'docker.chameleoncloud.org'
    DOCKER_REGISTRY_CREDS = credentials('kolla-docker-registry-creds')
  }

  stages {
    stage('docker-setup') {
      steps {
        sh 'docker login --username=$DOCKER_REGISTRY_CREDS_USR --password=$DOCKER_REGISTRY_CREDS_PSW $DOCKER_REGISTRY'
      }
    }
    stage('build-and-publish') {
      steps {
        sh 'make build'
        sh 'make publish'
      }
    }
  }

  post {
    always {
      sh 'docker logout $DOCKER_REGISTRY'
    }
  }
}
