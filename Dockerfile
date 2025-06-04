FROM devops-automation-docker.artifactory.techopscloud.com/org.xyz.devops.baseimage/ubi9-python-311
#FROM devops-automation-docker.artifactory.techopscloud.com/org.xyz.devops.baseimage/ubi8-python3
ARG ARTIFACTORY-artifactory.techopscloud.com
ARG ARTIFACTORY_API_USER
ARG ARTIFACTORY_AUTH_TOKEN

ENV http_proxy=http://proxy.ops.xyz.org:8080/ \
    https_proxy=http://proxy.ops.xyz.org:8080/ \
    no_proxy=localhost,127.0.0.1,.techopscloud.com,.xyz.org,docker-test-local.testartifactory.test.xyz.org,artifactory.techopscloud.com,dendvb3utdoe06.cloud.xyz.org,.eks.amazonaws.com

USER root
RUN python -m venv $VIRTUAL_ENV \
    && pip install -r requirements.txt -i https://$ARTIFACTORY API USER:SARTIFACTORY AUTH TOKEN@SARTIFACTORY/artifactory/api/pypi/pypi-xyz-remote/simple

RUN mkdir -p ./temp

COPY . /app/

#RUN 1s -Irth
#RUN cd /app
#RUN Is -Irth

#RUN yum install nvidia-xconfig

#RUN rpm -i /app/app/web_crawler/driver/chromium-common-135.0.7049.95-1.e19.x86_64.rpm
#RUN rpm -1 /app/app/web_crawler/driver/chromedriver-135.0.7049.95-1.e19.x86_64.rpm

ENV HTTP_PROXY="" HTTPS_PROXY=""http_proxy="" https_proxy="" NO_PROXY="" no_proxy=""
USER 1001
CMD ["uvicorn", "wsgi:app", " -- host", "0.0.0.0"," -- port", "8083", " -- workers", "4"]