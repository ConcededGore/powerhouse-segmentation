import os
import argparse
import SimpleITK as sitk

def main():
    args = getArgs()
    medianRadius = args.median
    topHatRadius = args.tophat_radius
    minSize = args.minsize

    images = getImages(args.images)

    viewer = sitk.ImageViewer()
    viewer.SetApplication(args.viewer)

    # notes: use aggressive median filter to remove noise
    # structures of interest are the most dense, so remove things of lower density
    for img_orig in images:
        # seems to work ok
        # img = sitk.Median(img, radius=(10, 10))
        # img = sitk.SmoothingRecursiveGaussian(img, sigma=5.)
        # img = sitk.LaplacianSharpening(img)
        # img = sitk.BinaryThreshold(img, lowerThreshold=180, upperThreshold=255, outsideValue=0)
        # img = sitk.ConnectedComponent(img)

        img = sitk.Median(img_orig, radius=(medianRadius, medianRadius)) # param
        #img = sitk.SmoothingRecursiveGaussian(img_orig, sigma=10)
        img = sitk.LaplacianSharpening(img)
        img = sitk.WhiteTopHat(img, kernelRadius=(topHatRadius, topHatRadius)) # param
        img = sitk.OtsuThreshold(img, 0, 1)
        img = sitk.ConnectedComponent(img)

        img_labelMap = sitk.RelabelComponent(img, minimumObjectSize=minSize) # param

        overlay  = sitk.LabelMapOverlay(sitk.Cast(img_labelMap, sitk.sitkLabelUInt32), img_orig, opacity=.85)
        labels = sitk.LabelToRGB(img_labelMap)

        # print(img_rgb.GetPixelIDTypeAsString())
        # print(img_orig.GetPixelIDTypeAsString())


        viewer.Execute(overlay)
        viewer.Execute(labels)

def getArgs():
    # parse arguments
    parser = argparse.ArgumentParser(
        description="powerhouse segmentation image processing"
    )

    # Users choice of image viewer
    parser.add_argument(
        "--viewer",
        "-v",
        nargs="?",
        help='path to image viewer, default value is "Fiji"',
        default="Fiji",
    )

    # List of image files to process
    parser.add_argument(
        "images", metavar="IMG", nargs="+", help="image filename(s) to process"
    )

    # Median Radius
    parser.add_argument(
        "--median",
        "-m",
        nargs="?",
        help="radius of the structuring element used in the median filter",
        type=int,
        default=7,
    )

    # White Top Hat Radius
    parser.add_argument(
        "--tophat_radius",
        "-t",
        nargs="?",
        help="radius of the structuring element used in the White TopHat algorithm",
        type=int,
        default=10,
    )

    # Minimum size of the final labels
    parser.add_argument(
        "--minsize",
        "-s",
        nargs="?",
        help="remove any labels that are below the specified size",
        type=int,
        default=600,
    )

    return parser.parse_args()



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

