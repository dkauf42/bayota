import os
import docker

from bayota_settings.base import get_bayota_version, get_model_instances_dir, \
    get_scripts_dir, get_spec_files_dir, get_control_dir, get_model_specs_dir

docker_client = docker.from_env()

# Paths are specified and mapped to 'incontainer' directories
docker_image = 'bayota_conda_app'

incontainer_workspace = '/root/bayota_ws'
incontainer_control_dir = incontainer_workspace + '/control'
incontainer_specfiles_dir = incontainer_workspace + '/specification_files'
incontainer_modelinstances_dir = incontainer_workspace + '/temp/specification_files'

volumes_dict = {f"{get_control_dir()}": {'bind': f"{incontainer_control_dir}", 'mode': 'rw'},
                f"{get_spec_files_dir()}": {'bind': f"{incontainer_specfiles_dir}", 'mode': 'rw'},
                f"{get_model_instances_dir()}": {'bind': f"{incontainer_modelinstances_dir}", 'mode': 'rw'}}

print(volumes_dict)
print(type(volumes_dict))

# Job command is composed.
model_generator_script = '/root/bayota/bin/slurm_scripts/run_step2_generatemodel.py'
study_control_file = os.path.join(incontainer_control_dir, 'step1_studycon65929049-0ceb-46aa-a002-9bb8804175ae.yaml')
CMD = f"{model_generator_script} -cf {study_control_file}"
print(f'Job command is: "{CMD}"')

# Job command is run in docker image.
response = docker_client.containers.run('bayota_conda_app', CMD, volumes=volumes_dict)
