from typing import Iterable, Tuple, List

from primitives import Polygon
from . raster_state import RasterState


def get_scanline_bucket(poly: Polygon) \
     -> Tuple[List[int], List[List[RasterState]]]:
    """
    This function generates AET bucket required for the scanline rasterizer
    to work.
    """

    if len(poly.points) < 3:
        raise ValueError("polygon object must have at least three points")

    bucket_idx: List[int] = []
    bucket_val: List[List[RasterState]] = []

    # -- fill the bucket
    for e in poly.lines_iter():
        dt = e.delta()

        if dt.y == 0:
            continue

        if dt.y < 0:
            e.swap_points()
            dt.invert()  # don't invert?

        esy, eey = e.start.y, e.end.y
        ymin = min(esy, eey)
        ymax = max(esy, eey)

        if ymin == esy:
            x = e.start.x
        else:
            x = e.end.x

        if ymin not in bucket_idx:
            bln = len(bucket_idx)
            idx = 0

            if bln == 0:
                bucket_idx.append(ymin)
                bucket_val.append([])
            else:
                while idx < bln and bucket_idx[idx] < ymin:
                    idx += 1

                bucket_idx.insert(idx, ymin)
                bucket_val.insert(idx, [])
        else:
            idx = bucket_idx.index(ymin)

        bucket_val[idx].append(RasterState(e, ymax, x, dt.x, dt.y))

    return bucket_idx, bucket_val


def get_raster_lines(
    bucket_idx: List[int],
    bucket_val: List[List[RasterState]]
) -> Iterable[Tuple[int, int]]:
    """
    `get_raster_lines` yields a tuple of three integers, denoting start
    and end position to fill with color: (y, x1, x2)
    """

    bln = len(bucket_idx)
    if bln <= 0:
        return

    # -- process the bucket
    y: int = bucket_idx.pop(0)  # current y
    sets: List[RasterState] = []

    bln -= 1  # popped

    tmp: List[RasterState] = bucket_val.pop(0)
    sln = len(tmp)

    # SORT sets
    if sln > 0:
        sets.append(tmp[0])

        sln -= 1

        for st in tmp[1:]:
            idx = 0

            while idx < len(sets) and sets[idx].x < st.x:
                idx += 1

            sets.insert(idx, st)

    sln = len(sets)
    deletes: List[RasterState] = []

    while sln > 0:
        # 1. delete "single" expired edges
        if sln > 0:
            deletes = []

            i = 0
            while i < sln:
                n = i
                i += 1
                nx = i % sln

                rs1 = sets[n]
                rs2 = sets[nx]

                # FIXME process "single" deletes
                if rs2 not in deletes and rs2.edge.start.y == y:
                    # side: end == start, start == end
                    if rs1.edge.end == rs2.edge.start:
                        deletes.append(rs1)
                    elif rs1.edge.start == rs2.edge.end:
                        deletes.append(rs2)
                elif rs1 not in deletes and rs1.edge.end.y == y:
                    if rs1.edge.start == rs2.edge.start:  # V shape
                        deletes.append(rs1)
                    elif rs1.edge.end == rs2.edge.end:  # Inverted V shape
                        # print("INVERTED V:", sets)  # TODO remove debugging
                        yield rs1.x, y
                        # deletes.append(rs1)
                        # deletes.append(rs2)
                    else:
                        # FIXME additional conditionals
                        deletes.append(rs1)
                elif rs2 not in deletes and rs2.edge.end.y == y:
                    if rs1.edge.start == rs2.edge.start:  # V shape
                        # print("V:", sets)  # TODO remove debugging
                        # yield rs2.x, y
                        # yield rs2.x, y
                        deletes.append(rs2)

            for st in deletes:
                sets.remove(st)

        # 2. insert new edges from SET
        if bln > 0 and y == bucket_idx[0]:
            bucket_idx.pop(0)
            sets += bucket_val.pop(0)
            bln = len(bucket_idx)

        # FIXME ??
        sln = len(sets)
        if sln <= 0:
            break

        # 3. draw lines
        for st in sets:
            yield (st.x, y)

        # 4. delete "double" expired edges
        # TODO.
        deletes = []

        for st in sets:
            if st.y_max <= y:
                deletes.append(st)

        for st in deletes:
            sets.remove(st)

        # 5. update current sets
        for st in sets:
            st.remainder += st.dx

            if st.dx >= 0:
                while 2 * st.remainder >= st.dy:
                    st.x += 1
                    st.remainder -= st.dy
            else:
                while -2 * st.remainder >= st.dy:
                    st.x -= 1
                    st.remainder += st.dy

        # 6. sort current sets
        nst: List[RasterState] = []
        ln = len(sets)

        if ln > 0:
            nst.append(sets[0])

            for st in sets[1:]:
                idx = 0

                while idx < len(nst) and nst[idx].x < st.x:
                    idx += 1

                nst.insert(idx, st)

        sets = nst
        sln = len(sets)
        y += 1
