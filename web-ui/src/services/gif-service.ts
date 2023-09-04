import { HttpStatusCode } from "axios";
import apiClient from "./api-client";

class GifService {
    constructor() {
    }

    gifUrl(s3_keys: string[]) { 
        const requestData = {gifKeys: s3_keys}
        const request = apiClient.post('/gif_url',requestData )
        return {request}
    }

    listS3Keys(continuationToken: string | null) { 
        let requestData = {}
        if (continuationToken) {
            requestData = {continuationToken: continuationToken}
        }

        const request = apiClient.post('/list_s3_keys',requestData, {
            headers: {
                'Content-Type': 'application/json',
            }
        } )
        return {request}
    }
}

const create = () => new GifService();
export default create();