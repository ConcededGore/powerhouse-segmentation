import os
import argparse
import SimpleITK as sitk

def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='powerhouse segmentation image processing')
    parser.add_argument('--viewer', '-v', nargs='?', help='path to image viewer, default value is "Fiji"')
    parser.add_argument('images', metavar='IMG', nargs='+', help='image filename(s) to process')
    args = parser.parse_args()

    images = getImages(args.images)

    viewer = sitk.ImageViewer()
    app = 'Fiji'
    if args.viewer != None:
        app = args.viewer
    viewer.SetApplication(app)

    # TODO: put actual code here, right now just opens the images
    for i in range(len(images)):
        viewer.Execute(images[i])


# args: list of strings (filenames)
# returns: array of sitk images
# 
def getImages(args):
    images = []
    for fn in args:
        if os.path.isdir(fn) or not os.path.exists(fn):
            print('filename is a directory or does not exist: ', fn)
            args.remove(fn)
        else:
            try:
                images.append(sitk.ReadImage(fn))
            except RuntimeError as e:
                print(e)
            
    return images

if __name__ == '__main__':
    main()