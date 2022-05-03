import os
import argparse
import SimpleITK as sitk

def main():
    # parse arguments
    parser = argparse.ArgumentParser(
        description="powerhouse segmentation image processing"
    )
    parser.add_argument(
        "--viewer",
        "-v",
        nargs="?",
        help='path to image viewer, default value is "Fiji"',
        default="Fiji",
    )
    parser.add_argument(
        "images", metavar="IMG", nargs="+", help="image filename(s) to process"
    )
    args = parser.parse_args()

    images = getImages(args.images)

    viewer = sitk.ImageViewer()
    #viewer.SetApplication(args.viewer)

    # notes: use aggressive median filter to remove noise
    # structures of interest are the most dense, so remove things of lower density
    for img_orig in images:
        # seems to work ok
        # img = sitk.Median(img, radius=(10, 10))
        # img = sitk.SmoothingRecursiveGaussian(img, sigma=5.)
        # img = sitk.LaplacianSharpening(img)
        # img = sitk.BinaryThreshold(img, lowerThreshold=180, upperThreshold=255, outsideValue=0)
        # img = sitk.ConnectedComponent(img)

        img = sitk.Median(img_orig, radius=(7, 7))
        #img = sitk.SmoothingRecursiveGaussian(img_orig, sigma=10)
        img = sitk.LaplacianSharpening(img)
        img = sitk.WhiteTopHat(img, kernelRadius=(10, 10))
        img = sitk.OtsuThreshold(img, 0, 1)
        img = sitk.ConnectedComponent(img)

        img_labelMap = sitk.RelabelComponent(img, minimumObjectSize=600)

        img_rgb = sitk.LabelToRGB(img)

        # print(img_rgb.GetPixelIDTypeAsString())
        # print(img_orig.GetPixelIDTypeAsString())

        img_overlay = sitk.LabelMapOverlay(sitk.Cast(img_labelMap, sitk.sitkLabelUInt32), img_orig, opacity=.85)

        viewer.Execute(img_overlay)



# args: list of strings (filenames)
# returns: array of sitk images
#
def getImages(args):
    images = []
    for fn in args:
        if os.path.isdir(fn) or not os.path.exists(fn):
            print("filename is a directory or does not exist: ", fn)
            args.remove(fn)
        else:
            try:
                images.append(sitk.ReadImage(fn))
            except RuntimeError as e:
                print(e)

    return images


if __name__ == "__main__":
    main()

