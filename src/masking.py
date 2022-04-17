import SimpleITK as sitk

def create_median_close_mask(img, median_iters=3, median_radius=5, binary_thresh=20, close_radius=5, display_mask=False):

    if median_iters > 1:
        median_filter = sitk.MedianImageFilter()
        median_filter.SetRadius(median_radius)
        median = median_filter.Execute(img)

    for i in range(1, median_iters):
        median = median_filter.Execute(median)

    # Convert median into binary
    for i in range(median.GetSize()[0]):
        for j in range(median.GetSize()[1]):
            if median.GetPixel(i, j) > binary_thresh:
                median.SetPixel(i, j, 1)
            else:
                median.SetPixel(i, j, 0)

    close_aperature = sitk.BinaryMorphologicalClosingImageFilter()
    close_aperature.SetKernelRadius(close_radius)
    closed = close_aperature.Execute(median)

    if display_mask:
        view_img = sitk.Image(closed.GetSize()[0], closed.GetSize()[1], sitk.sitkUInt8)

        # Make it visible again
        for i in range(closed.GetSize()[0]):
            for j in range(closed.GetSize()[1]):
                if closed.GetPixel(i, j) == 1:
                    view_img.SetPixel(i, j, 255)

        sitk.ImageViewer().Execute(view_img)

    return closed


def apply_mask(img, mask):
    retval = sitk.Image(img.GetSize()[0], img.GetSize()[1], sitk.sitkUInt8)

    if img.GetSize() != mask.GetSize():
        print("ERROR: IMG SIZE AND MASK SIZE MUST BE EQUAL")
        return

    for i in range(img.GetSize()[0]):
        for j in range(img.GetSize()[1]):
            if mask.GetPixel(i, j) != 0:
                retval.SetPixel(i, j, img.GetPixel(i, j))

    return retval

