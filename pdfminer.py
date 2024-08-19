from pathlib import Path
from typing import Iterable, Any

from pdfminer.layout import LTTextLineHorizontal, LAParams, LTPage, LTChar
from pdfminer.high_level import extract_pages
from pdfminer.pdfpage import PDFPage

def normal_search_and_sign(path, search):

    #print('Searching: ', search)

    #path = Path(path).expanduser() #get path with user
    o = extract_pages(path) #extract pages

    stack = [(o, 0)]
    found_bboxes = {}

    while stack:
        current, pagenum = stack.pop()

        if isinstance(current, Iterable):
            for i in current:
                """ LTPage means page number in pdf """
                if isinstance(i, LTPage): #check if there's LTPage
                    pagenum += 1 #increments pagenum
                    #print(f"Searching {search} in page {pagenum}")

                """ checks if there's a horizontal text """
                if isinstance(i, LTTextLineHorizontal) and hasattr(i, 'bbox'):
                    if i.get_text().strip() == search or i.get_text().strip() == ' '.join(search):
                        #print(f"Found {search} in page {pagenum}.")
                        if pagenum not in found_bboxes:
                            found_bboxes[pagenum] = []
                        found_bboxes[pagenum].append(i.bbox)

                stack.append((i, pagenum))

    return found_bboxes

def autocad_search_and_sign(path, search):

    #print('Searching: ', search)

    path = Path(path).expanduser() #get path with user
    o = extract_pages(path) #extract pages

    stack = [(o, 0)]
    found_bboxes = {}
    origin_element = None

    element = {}
    origin = []

    while stack:
        current, pagenum = stack.pop()

        if isinstance(current, Iterable):
            for i in current:
                """ LTPage means page number in pdf """
                if isinstance(i, LTPage): #check if there's LTPage
                    pagenum += 1 #increments pagenum

                    """
                        Only searches on page 1
                        Break the loop in page > 1
                    """
                    if pagenum > 1:
                        break
                    # print(f"Searching {search} in page {pagenum}")

                """ checks if there's a horizontal text """
                if isinstance(i, LTTextLineHorizontal) and hasattr(i, 'bbox'):
                    if i.get_text().strip() == 'OFFICE OF THE BUILDING OFFICIAL' or i.get_text().strip() == 'OFFICE OF THE BUILDING OFFICIALS': #checks if the text in the text line is equal to the search param
                        origin_element = i

                        """ logs all coordinates found in that page """
                        #if pagenum not in found_bboxes:
                        #    found_bboxes[pagenum] = []
                        #found_bboxes[pagenum].append(i.bbox)
                    elif i.get_text().strip() in search: # or i.get_text().strip() == ' '.join(search):
                        #print(f"Found {search} in page {pagenum}.")
                        if pagenum not in element:
                            element[pagenum] = []
                        element[pagenum].append(i)

                stack.append((i, pagenum))

    if(origin_element):
        origin_bboxes = get_x_in_bbox(origin_element)

        for key, value in element.items():
            for index, i in enumerate(value):
                search_bboxes = get_x_in_bbox(i)
                aligned_x = is_aligned(search_bboxes, origin_bboxes)
                if aligned_x:
                    if key not in found_bboxes:
                        found_bboxes[key] = []
                    list_bbox = list(i.bbox) # convert tupple to list
                    list_bbox[0] = aligned_x # replace the x coordinate of the element with the pivot x coordinate
                    list_bbox[2] = origin_element.bbox[2] # replace the x2 value of the element with the pivot x2 value
                    tupple_bbox = tuple(list_bbox)
                    found_bboxes[key].append(tupple_bbox)
    return found_bboxes

def is_aligned(arr, origin):
    maxbox = max(origin)
    minbox = min(origin)

    for i in arr:
        if i <= maxbox and i >= minbox:
            return i
    return False


def get_x_in_bbox(obj):
    x_coordinates = []
    for i in obj:
        if isinstance(i, LTChar) and hasattr(i, 'bbox'):
            #print(i)
            x_coordinates.append(i.bbox[0])

    return x_coordinates
