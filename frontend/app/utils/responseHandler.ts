import { AxiosResponse } from 'axios';

const handleApiResponse = <T>(response: AxiosResponse): T => {
  if (response.status >= 200 && response.status < 300) {
    return response.data;
  } else {
    throw new Error('API request failed with status: ' + response.status);
  }
};

export default handleApiResponse;
