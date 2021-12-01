import math

import cv2
import numpy as np

IM_WDTH = 500
IM_HGHT = 500

IM_C_X = int(IM_WDTH/2)
IM_C_Y = int(IM_HGHT/2)

TIME = 0.0

BKG_COLOR = (.35,.35,.35)

BLUE = (.8, .13, .1)
YELLOW = (.16, .6, .6)

def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result

def create_slice(slice_degrees, slice_color, hoop_outer_radius):
    slice_img = np.zeros((IM_HGHT,IM_WDTH,3))

    draw_tolerance = 1

    cv2.ellipse(slice_img, (IM_C_X,IM_C_Y), (hoop_outer_radius,hoop_outer_radius), 0, 0, 360, color=slice_color, thickness=-1)
    cv2.rectangle(slice_img, (0, IM_C_Y+draw_tolerance), (IM_HGHT, IM_WDTH), (0,0,0), -1)

    if slice_degrees == 180:
        return slice_img

    slice_img = rotate_image(slice_img, slice_degrees)
    cv2.rectangle(slice_img, (0, IM_C_Y+draw_tolerance), (IM_HGHT, IM_WDTH), (0, 0, 0), -1)

    return slice_img

def superimpose(base_image, black_image, offset):
    black_image_resized = np.zeros(base_image.shape)
    black_image_resized[offset[1]:offset[1] + black_image.shape[0], offset[0]:offset[0] + black_image.shape[1]] = black_image

    # print(black_image_resized.shape)

    # grey_black_img = cv2.cvtColor(np.float32(black_image_resized), cv2.COLOR_BGR2GRAY)
    #
    # # mask = cv2.inRange(black_image, (0,0,0), (3,3,3))
    # ret, bin_img = cv2.threshold(grey_black_img, 0, 5, cv2.THRESH_BINARY)
    #
    # print(bin_img.shape)
    # # mask = mask.astype(dtype=np.uint)
    # bin_img = bin_img.astype('int')
    # result = cv2.bitwise_and(base_image, black_image_resized, mask=bin_img)

    result = base_image + black_image_resized

    return result

def draw_hoop(image, position, radius, thickness, repeats, angle_offset):
    colors = [BLUE, YELLOW]
    num_colors = 2
    num_repeats = repeats

    hoop_outer_radius = radius
    hoop_inner_radius = radius - thickness

    hoop_img = np.zeros((IM_WDTH,IM_HGHT,3))
    # first create the slices
    slice_degrees = 360/(num_colors * num_repeats)
    # blue_slice = create_slice(slice_degrees, BLUE, hoop_outer_radius)
    # yellow_slice = create_slice(slice_degrees, YELLOW, hoop_outer_radius)

    # assemble the pie
    for repetition in range(num_repeats):
        for col in range(num_colors):
            hoop_img += create_slice(slice_degrees, colors[col], hoop_outer_radius)
            hoop_img = rotate_image(hoop_img, slice_degrees)

    # cut out the middle
    cv2.ellipse(hoop_img, (IM_C_X+position[0], IM_C_Y), (hoop_inner_radius,hoop_inner_radius), 0, 0, 360, (0,0,0), -1)

    # superimpose hoop on background
    hoop_img = rotate_image(hoop_img, TIME)
    hoop_img = rotate_image(hoop_img, angle_offset)

    # result_im = superimpose(bkg, hoop_img, (position[0],position[1]))
    return hoop_img

def superimpose_hoop(bkg, hoop_im, hoop_rad, hoop_thickness):
    mask = np.zeros((IM_HGHT, IM_WDTH), dtype="uint8")
    cv2.circle(mask, (IM_C_X, IM_C_Y), hoop_rad, 255, -1)
    cv2.circle(mask, (IM_C_X, IM_C_Y), hoop_rad-hoop_thickness, 0, -1)

    ret, inv = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
    m_inv = cv2.bitwise_not(inv)

    new_im = bkg.copy()

    # new_im[:,:] =
    # print(bkg.dtype)
    masked_bkg = cv2.bitwise_and(bkg, bkg,  mask=m_inv).astype(np.float64)
    # cv2.imshow("hi", mask)
    result = masked_bkg+hoop_im
    # cv2.imshow("hi", result)
    return result

if __name__ == '__main__':

    bkg = np.zeros((IM_HGHT, IM_WDTH, 3))
    # set background to grey
    bkg = cv2.rectangle(bkg, (0,0), (IM_WDTH, IM_HGHT), BKG_COLOR, -1)

    hoop_radius = 145
    hoop_thickness = 40
    hoop_border_thickness = 3

    im_no_hoop = np.zeros((IM_HGHT, IM_WDTH, 3))
    big_hoop = draw_hoop(im_no_hoop, (0, 0), hoop_radius, hoop_thickness, 2, 0)
    outer_hoop = draw_hoop(im_no_hoop, (0, 0), hoop_radius-hoop_thickness, hoop_border_thickness, 2, 45)
    inner_hoop = draw_hoop(im_no_hoop, (0, 0), hoop_radius+hoop_border_thickness, hoop_border_thickness, 2, -45)

    hooped_im = big_hoop + outer_hoop + inner_hoop

    is_inverted = False
    is_paused = False
    while True:

        new_hooped_im = rotate_image(hooped_im, TIME)

        hoop_with_bkg = superimpose_hoop(bkg, new_hooped_im, hoop_radius+hoop_border_thickness, hoop_thickness+(2*hoop_border_thickness))
        # hooped_im = draw_hoop(hooped_im, (150, 0))
        cv2.imshow('hoops', hoop_with_bkg)

        timestep = 3

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord('i'):
            is_inverted = not is_inverted
        if key == ord(' '):
            is_paused = not is_paused
        if not is_paused:
            if is_inverted:
                TIME -= timestep
            else:
                TIME += timestep



