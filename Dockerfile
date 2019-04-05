FROM python:3.7-slim-stretch

# set up users and directories
ENV PROJECT pyspaceship
ENV HOME /srv/$PROJECT
ENV USER $PROJECT
RUN adduser --system --group --home $HOME --disabled-password $USER
USER $USER

# create the place where the secrets will go
RUN mkdir $HOME/secrets
VOLUME $HOME/secrets

# the place where the code will go
ENV CODE_DIR $HOME/code
RUN mkdir $CODE_DIR
WORKDIR $CODE_DIR

## want the binaries installed with 'pip --user' in the PATH
ENV PATH "$HOME/.local/bin:$PATH"

# install python dependencies
COPY ./requirements.txt .
RUN pip install --user -r requirements.txt

# copy the code into the image!
COPY . $CODE_DIR

# set this to 'production' in production deploys
ENV ENVIRONMENT dev

ENTRYPOINT ["gunicorn", "spaceship:app", "--access-logfile", "-"]

CMD ["--bind", "0.0.0.0:9876"]
EXPOSE 9876/tcp
