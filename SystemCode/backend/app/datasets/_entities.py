import os
from uuid import uuid4
import tarfile

from ..entities import session_scope, Dataset
from ._utils import dataset_dir


def get_dataset(uuid):
  with session_scope() as session:
    dataset = session.query(Dataset).filter_by(uuid=uuid).first()
    if dataset is not None:
      return (dataset.uuid, dataset.name)
    else:
      return (None, None)


def get_datasets(type):
  with session_scope() as session:
    datasets = session.query(Dataset).filter_by(type=type).order_by(Dataset.name).all()
    arr = []
    for m in datasets:
      arr.append({
        'key': m.uuid,
        'uuid': m.uuid,
        'type': m.type,
        'name': m.name,
        'label': m.label,
        'status': m.status
      })
    return arr


def create_dataset(**props):
  with session_scope() as session:
    dataset = Dataset(**props)
    session.add(dataset)


def update_dataset(uuid, status):
  with session_scope() as session:
    dataset = session.query(Dataset).filter_by(uuid=uuid).first()
    if dataset is not None:
      dataset.status = int(status)
      return {'uuid': uuid, 'status': status}
    else:
      return {'uuid': uuid}


def delete_dataset(uuid):
  with session_scope() as session:
    dataset = session.query(Dataset).filter_by(uuid=uuid).first()
    if dataset is not None:
      session.delete(dataset)
      return {'uuid': uuid, 'type': dataset.type, 'name': dataset.name, 'label': dataset.label}
    else:
      return {'uuid': uuid}


def upload_dataset(type, name, label, filepath):
  uuid = uuid4()

  filetype = f".{filepath.split('.')[-1]}"
  filename = f"{name}_{uuid}{filetype}"
  dsdir = dataset_dir(f"{name}_{uuid}")
  dspath = os.path.join(dsdir, filename)
  os.rename(filepath, dspath)

  arc_path = os.path.join(dataset_dir('__archive__'), filename)

  if tarfile.is_tarfile(dspath):
    with tarfile.open(dspath) as tf:
      def is_within_directory(directory, target):
          
          abs_directory = os.path.abspath(directory)
          abs_target = os.path.abspath(target)
      
          prefix = os.path.commonprefix([abs_directory, abs_target])
          
          return prefix == abs_directory
      
      def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
      
          for member in tar.getmembers():
              member_path = os.path.join(path, member.name)
              if not is_within_directory(path, member_path):
                  raise Exception("Attempted Path Traversal in Tar File")
      
          tar.extractall(path, members, numeric_owner=numeric_owner) 
          
      
      safe_extract(tf, path=dsdir)
    os.rename(dspath, arc_path)
  else:
    # todo - support other formats
    os.rename(dspath, arc_path)
    return {'uuid': uuid}

  create_dataset(uuid=uuid, type=type, name=name, label=label, status=1)
  return {'uuid': uuid, 'type': type, 'name': name, 'label': label}

