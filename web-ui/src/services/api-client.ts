import axios, {CanceledError} from "axios";

export default axios.create({
    baseURL: "https://eaqx59qktb.execute-api.us-east-1.amazonaws.com/prod/",
})