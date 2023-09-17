import axios, {CanceledError} from "axios";
import config from "../../config";

export default axios.create({
    baseURL: config.apiDomain,
})