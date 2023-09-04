import { SetStateAction, useState, useEffect } from "react";
import "./App.css";
import GifCard from "./components/GifCard";
import NavBar from "./components/NavBar";
import GifService from "./services/gif-service";
import { AxiosResponse } from "axios";
import { datadogRum } from "@datadog/browser-rum";

datadogRum.init({
  applicationId: "6e52b0d2-afce-43a1-9ab1-313bd11978b5",
  clientToken: "pubf84f9b443b272143e11a8d74ce613ee3",
  site: "datadoghq.com",
  service: "soap-gif-splitter",
  env: "tara-cloud",
  // Specify a version number to identify the deployed version of your application in Datadog
  // version: '1.0.0',
  sessionSampleRate: 100,
  sessionReplaySampleRate: 20,
  trackUserInteractions: true,
  trackResources: true,
  trackLongTasks: true,
  defaultPrivacyLevel: "mask-user-input",
});

datadogRum.startSessionReplayRecording();

function App() {
  const [error, setError] = useState<string>("");
  const [gifUrls, setGifUrls] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [continuationToken, setContinuationToken] = useState<string | null>(
    null
  );

  const getS3Keys = async (continuationToken: string | null) => {
    console.log("Getting s3 Keys");
    try {
      const { request } = GifService.listS3Keys(continuationToken);
      const response = await request;
      console.log("Got keys: " + response.data.s3_keys);
      return response; // Return the response promise
    } catch (err: any) {
      setError(err.message);
      console.log(err.message);
    }
  };

  const getGifUrls = async (s3Keys: string[]) => {
    console.log("Getting URLs");
    try {
      const { request } = GifService.gifUrl(s3Keys);
      const response = await request;
      console.log("Got URLs: " + response.data.presignedUrls);
      return response; // Return the response promise
    } catch (err: any) {
      setError(err.message);
      console.log(err.message);
    }
  };

  async function fetchData() {
    console.log("Fetching data with token:" + continuationToken);
    try {
      const response: AxiosResponse | undefined = await getS3Keys(
        continuationToken
      ); // Await the getS3Keys function
      if (response) {
        const gifKeys: string[] = response.data.s3_keys; // Get the data from the response
        setContinuationToken(response.data.next_token); // Set the continuation token
        try {
          const gifUrlsResponse: AxiosResponse | undefined = await getGifUrls(
            gifKeys
          ); // Await the getGifUrls function
          if (gifUrlsResponse) {
            setGifUrls(gifUrlsResponse.data.presignedUrls); // Set the gifUrls state
            setIsLoading(false); // Set the isLoading state
          }
        } catch (err: any) {
          console.log(err.message);
        }
      }
    } catch (err: any) {
      console.log(err.message);
    }
  }

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <>
      <NavBar></NavBar>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 mt-10">
        {isLoading ? (
          <p>Loading...</p>
        ) : (
          gifUrls.map((key, index) => (
            <GifCard
              key={key} // Add a unique key prop for mapping purposes
              gifURL={gifUrls[index]}
              gifKey="placeholder"
            />
            // <img src={gifUrls[index]} alt="gif" key={key} />
          ))
        )}
      </div>
      <button onClick={() => fetchData()} disabled={isLoading}>
        Load More
      </button>
    </>
  );
}

export default App;
