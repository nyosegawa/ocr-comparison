export interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Annotation {
  id: string;
  rect: Rect;
  text: string;
  createdAt: string;
  updatedAt: string;
}

export interface ImageAnnotationData {
  imageId: string;
  imagePath: string;
  originalPath?: string;
  width: number;
  height: number;
  annotations: Annotation[];
}

export interface ImageInfo {
  id: string;
  filename: string;
  originalFilename: string;
  path: string;
  originalPath: string;
  width: number;
  height: number;
  originalWidth: number;
  originalHeight: number;
  preprocessed: boolean;
  uploadedAt: string;
}
