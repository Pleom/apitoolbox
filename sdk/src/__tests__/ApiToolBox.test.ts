import { ApiToolBox } from '../ApiToolBox';

describe('ApiToolBox', () => {
  let sdk: ApiToolBox;

  beforeEach(() => {
    sdk = new ApiToolBox();
  });

  it('should create an instance of ApiToolBox', () => {
    expect(sdk).toBeInstanceOf(ApiToolBox);
  });
});
