# Dockerfile for Bayota
#
# Files to exclude are listed in the ./dockerignore file
#
# Example commands...
#
#  Create a docker image:
#     >> docker build -f Dockerfile_conda3_thenIpopt --tag bayota_conda_then_ipopt_app .
#
#    -- Create a first-stage docker image from the 'builder' stage:
#       >> docker build -f Dockerfile_conda3_thenIpopt --tag bayota_app_builder . --target builder
#    -- Create a second-stage docker image from the 'builder2' stage:
#       >> docker build -f Dockerfile_conda3_thenIpopt --tag bayota_app_builder2 . --target builder2
#
#
#  MANAGE IMAGES
#
#  Inspect the available docker images:
#     >> docker images
#
#  Delete/remove existing image <by Image ID> listed in "docker images"
#     >> docker rmi <imageID>
#     >> docker rmi ef9a50d6e1a2
#
#
#  RUNNING
#
#  Run a docker image in interactive mode (to see file directory structure):
#     >> docker run -it <imageID> sh
#  Run interactively, but also set up for running Bayota by passing environment variables and mounting directories.
#     >> docker run -it -e "BAYOTA_WORKSPACE_HOME" -v /Users/Danny/bayota_ws_0.1b1.dev2:/Users/Danny/bayota_ws_0.1b1.dev2 bayota_conda_app sh
#
#  Mount a host directory when running (add -v argument):
#     >> docker run -v /host/directory:/container/directory -it <imageID>
#
#  Test commands to pass to docker container:
#    -- Generate a model:
#     >> docker run -it <imageID> ./bin/scripts_by_level/run_generatemodel.py -g CalvertMD -n costmin_total_percentreduction -sf ~/bayota_ws_0.0a1.dev4/temp/model_instances/modelinstance_costmin_total_percentreduction_CalvertMD.pickle -bl 2010NoActionLoads.csv
#    -- Solve a model trial:
#     >> docker run -it <imageID> ./bin/scripts_by_level/run_conductexperiment.py -n /root/bayota/bin/run_specs/experiment_specs/costmin_1-40percentreduction -sf /root/bayota_ws_0.0a1.dev4/temp/model_instances/modelinstance_costmin_total_percentreduction_CalvertMD.pickle

# #################################################
# --- START ---
# #################################################
FROM continuumio/miniconda3 as builder
# Add the IPOPT directory generated in the `builder` container above
#COPY --from=builder /CoinIpopt /CoinIpopt

# Setup Conda Environment
RUN conda update -n base -c defaults conda -y
RUN conda create --name bayota3
# Activate Environment
# Pull the environment name out of the environment.yml
RUN echo "conda activate bayota3" > ~/.bashrc
ENV PATH /opt/conda/envs/bayota3/bin:$PATH
RUN conda clean -afy

# Do not install user tools on unmanaged images
# add vim for basic editing and checking
# RUN apt-get update && apt-get install vim -y

# --- Install basic requirements ---
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    gfortran \
    patch \
    make \
 && rm -rf /var/lib/apt/lists/*

# --- Get the IPOPT code ---
WORKDIR /
RUN curl --remote-name https://www.coin-or.org/download/source/Ipopt/Ipopt-3.12.12.tgz \
    \
    && tar -xvzf Ipopt-3.12.12.tgz \
    && mv /Ipopt-3.12.12 /CoinIpopt

# --- Download external code packages ---
RUN cd /CoinIpopt/ThirdParty/Blas \
    \
    && ./get.Blas \
    && cd ../Lapack \
    && ./get.Lapack \
    && cd ../ASL \
    && ./get.ASL \
    && cd ../Mumps \
    && ./get.Mumps

# --- Run IPOPT configure script ---
RUN mkdir /CoinIpopt/build \
    && cd /CoinIpopt/build \
    \
    && /CoinIpopt/configure

# --- Build the IPOPT code ---
RUN ls -alht \
    && pwd \
    && cd /CoinIpopt/build \
    && make \
    && make test \
    && make install

# --- Set up Bayota ---
COPY . /root/bayota
WORKDIR /root/bayota

# -- set up default bayota path directories (needed for bayota install) --
ENV BAYOTA_HOME=/root/bayota
ENV BAYOTA_WORKSPACE_HOME=/root

# RUN python setup.py develop
RUN pip install .

# Remove in-container workspace... the workspace will be mounted from outside
#   otherwise, the paths will be internal, where there aren't files
#RUN rm -r /root/bayota_ws*

# --- Ensure IPOPT is in path variable ---
ENV PATH="${PATH}:/CoinIpopt/build/bin"

CMD ["/bin/echo", "executing CMD"]
