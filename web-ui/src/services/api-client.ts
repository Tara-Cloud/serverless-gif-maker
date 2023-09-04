import axios, {CanceledError} from "axios";

export default axios.create({
    baseURL: "https://gal744o7q9.execute-api.us-east-1.amazonaws.com/prod",
})