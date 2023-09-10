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
    
    tagGif(s3_key: string, tags: any) { 
        const requestData = {s3_key: s3_key, tags: tags}
        const request = apiClient.post('/tag_gif',requestData, {
            headers: {
                'Content-Type': 'application/json',
            }
        } )
        return {request}
    }

    archiveGif(s3_key: string) { 
        const requestData = {s3_key: s3_key}
        const request = apiClient.post('/archive_gif',requestData, {
            headers: {
                'Content-Type': 'application/json',
            }
        } )
        return {request}
    }
}

const create = () => new GifService();
export default create();