# Author: Mark Mendez
# Date: 01/27/2022


from math import ceil
from heapq import heappush


def kibs_to_bytes(kibs: int | float):
    """
    Simple conversion from MiB to bytes
    :param kibs: number of MiB
    :return: number of bytes
    """
    return kibs * 1024  # to bytes


def mibs_to_bytes(mibs: int | float):
    """
    Simple conversion from MiB to bytes
    :param mibs: number of MiB
    :return: number of bytes
    """
    return mibs * 1024 * 1024  # to KiB to bytes


def calculate_transmission_time_statistical_multiplexing(known_data: dict) -> list[tuple]:
    """
    Calculates transmission times for each file, in a continuous alternating-packet transmission network.
    The order of elements in known_data['file_sizes_bytes'] should reflect the turn order given to packet senders
        by the transmission medium.
    !!! Ignores processing and queuing delays
    !!! Assumes partial packets are padded to known_data['packet_payload_size_bytes']
    :param known_data: dict in the following form:
                      'total_link_rate_Mbps': int or float,
                      'sharing_computers_count': int,  # Should match len(file_sizes_bytes).
                      #                                  For now, only 1 file per computer
                      'starting_time_seconds': int or float,
                      'file_sizes_bytes': [
                          int or float,
                          ...
                      ],
                      'packet_payload_size_bytes': int or float,
                      'packet_header_size_bytes': int or float
    :return: number of seconds for each file to finish transmitting, as a list of tuples,
             where index 0 is the time in seconds and index 1 is the turn order
    """
    # unpack known data
    total_link_rate_bps = known_data['total_link_rate_Mbps'] * 1000 * 1000  # convert to Kbps to bps
    sharing_computers_count = known_data['sharing_computers_count']
    starting_time_seconds = known_data['starting_time_seconds']
    file_sizes_bytes = known_data['file_sizes_bytes']
    packet_payload_size_bytes = known_data['packet_payload_size_bytes']
    packet_header_size_bytes = known_data['packet_header_size_bytes']

    # calculate number of packet payloads needed to send each file (rounding up because of assumed padding)
    needed_packets = [ceil(size_in_bytes / packet_payload_size_bytes) for size_in_bytes in file_sizes_bytes]

    # calculate total size per packet
    total_packet_size_bits = (packet_header_size_bytes + packet_payload_size_bytes) * 8  # * 8 to convert to bits

    # make a list (heapq for efficiency) of turn-order indices of files in size order (small to large)
    file_order_indices_by_needed_packets_asc = []
    for turn_order, packet_count in enumerate(needed_packets):
        heappush(file_order_indices_by_needed_packets_asc, (packet_count, turn_order))  # sort by size but pair with index
        #                                                                       (docs say turn_order is a tie-breaker)

    # Calculate the number of packets that will have been sent when each file finishes transmitting,
    #     iterating in size order (because the smallest packet finishes transmitting first, etc)
    # Calculate the first one separately to initialize
    packet_count = file_order_indices_by_needed_packets_asc[0][0]
    turn_order = file_order_indices_by_needed_packets_asc[0][1]
    total_packets_at_file_done = packet_count * sharing_computers_count
    total_packets_at_each_file_done = [total_packets_at_file_done]
    time_when_file_done_seconds = (
            total_packets_at_file_done
            * total_packet_size_bits
            / total_link_rate_bps
            + starting_time_seconds
    )
    times_at_each_packet_done_seconds = [(time_when_file_done_seconds, turn_order)]
    for index in range(1, len(file_order_indices_by_needed_packets_asc)):
        # this is the next smallest packet (rounded; post-rounding duplicates sorted by turn order)
        size_and_order = file_order_indices_by_needed_packets_asc[index]
        total_packets_needed_this_file = size_and_order[0]
        turn_order = size_and_order[1]
        total_packets_at_previous_done = total_packets_at_each_file_done[index - 1]

        # calculate total packets this file will wait for
        remaining_packets_this_file_at_previous_done = total_packets_needed_this_file - total_packets_at_previous_done
        total_packets_to_finish_this_file_at_previous_done = remaining_packets_this_file_at_previous_done * (sharing_computers_count - index)
        total_packets_at_file_done = total_packets_to_finish_this_file_at_previous_done + total_packets_at_previous_done

        # calculate total time for this file to finish
        time_when_file_done_seconds = (
                total_packets_at_file_done
                * total_packet_size_bits
                / total_link_rate_bps
                + starting_time_seconds
        )

        # add to output variable
        times_at_each_packet_done_seconds.append((time_when_file_done_seconds, turn_order))

    return times_at_each_packet_done_seconds


if __name__ == '__main__':
    # test
    known_data = {
        'total_link_rate_Mbps': 5.2,
        'sharing_computers_count': 2,  # should match len(file_sizes_bytes). For now, only 1 file per computer
        'starting_time_seconds': 0,
        'file_sizes_bytes': [
            mibs_to_bytes(3),
            kibs_to_bytes(165)
        ],
        'packet_payload_size_bytes': 1000,
        'packet_header_size_bytes': 24
    }

    result = calculate_transmission_time_statistical_multiplexing(known_data)
    print('transmission delay with statistical multiplexing:', result)
