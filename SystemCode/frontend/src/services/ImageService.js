import _ from 'lodash'
import axios from 'axios';
import {messageQueue} from './AppService';
import config from '../config';
import {getBackend, isValidModel} from '../adaptor'

export default class ImageService {
  constructor({baseUrl} = {}){
    this._baseUrl = `${config.backend.baseUrl}/image`;
    if(baseUrl){
      this._baseUrl = `${baseUrl}/image`;
    }
  }

  url = ({uuid, type, subdir = 'origin'}) => {
    return `${this._baseUrl}/${subdir}/${uuid}${type}`;
  }

  upload = async (file) => {
    let form = new FormData();
    form.append('image', file);

    let resp = await axios.post(this._baseUrl, form, {
      headers: {'Content-Type': 'multipart/form-data' }
    });
    return resp.data;
  }

  classify = async (req) => {
    let resp = await axios.post(`${this._baseUrl}/classify`, req);
    return resp.data;
  }

  detect = async (image) => {
    let result = await this.classify({
      type: 'real_fake', 
      image,
      model: config.backend.detector.model
    });
    return {
      image, result,
      info: [
        `I think this is a ${result.class} photo.`,
        `real: ${result.real.toFixed(4)} fake: ${result.fake.toFixed(4)}`
      ]
    }
  }

  generate = async ({name, version}) => {
    let resp = await axios.post(`${this._baseUrl}/generate`, {model: {name, version}});
    return resp.data;
  }

  postStats = async ({image, model:{name,version}, stats = []}) => {
    let resp = await axios.post(`${this._baseUrl}/stats`, {image, model: {name, version}, stats});
    return resp.data;
  }

  getStats = async () => {
    let resp = await axios.get(`${this._baseUrl}/stats`);
    return resp.data;
  }

  forModel = model => {
    let {backend} = config.getModel(model);
    if(!backend){
      return this;
    }
    //requires specific backend
    let {baseUrl} = getBackend(backend);
    if(!baseUrl){
      throw new Error(`no backend: ${backend}`);
    }
    return new ImageService({baseUrl});
  }

  //auto-adapt to multiple backends
  generateImage = async (models = []) => {
    //excluding model if no valid backend
    models = models.filter(isValidModel);

    if(models.length < 1){
      messageQueue.push({
        severity: "warning",
        title: "Model Not Selected",
        text: "Please enable at least one model for image generation",
        lifespan: 5000
      });
      return null;
    }
    let model = _.sample(models);
    let service = this.forModel(model);
    let image = await service.generate(model);
    return {
      ...image,
      url: service.url({...image, subdir: model.name})
    }
  }
}
