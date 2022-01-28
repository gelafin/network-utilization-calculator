# Author: Mark Mendez
# Date: 01/27/2022

def calculate_transmission_time(length_in_bytes: int, rate_in_Mbps: float) -> float:
    """
    Calculates network transmission time for a packet
    :param length_in_bytes: size of each packet --in bytes--
    :param rate_in_Mbps: transmission rate --in Mbps--
    :return: transmission time --in milliseconds--
    """
    packet_length = length_in_bytes
    rate = float(rate_in_Mbps)

    # convert all applicable values to bits
    packet_length *= 8  # from bytes to bits
    rate *= 1000 * 1000  # from Mbps to Kbps to bps

    # calculate transmission time in seconds
    transmission_time = float(packet_length) / rate

    # convert transmission time to milliseconds
    transmission_time *= 1000

    return transmission_time


def calculate_network_utilization(known_data: dict, window_size: int = None) -> float:
    """
    Calculates network utilization given some raw data
    :param known_data: dict containing the following data, with these keys
                       'length_in_bytes': (int) size of each packet --in bytes--
                       'rate_in_Mbps': (float) transmission rate --in Mbps--
                       'rtt_in_ms': (int) round-trip-time, or 2 * propagation delay, --in milliseconds--
    :param window_size: if using pipelining, set this to
                        the number of --bytes-- advertised as the receiver's window size
    :return: network utilization --in raw decimal--
    """
    # unpack known data
    packet_length = known_data['length_in_bytes']
    rate = known_data['rate_in_Mbps']
    rtt = float(known_data['rtt_in_ms'])

    # calculate transmission time in milliseconds
    transmission_time = calculate_transmission_time(packet_length, rate)

    # calculate total time
    total_time = transmission_time + rtt

    # calculate utilization
    utilization = transmission_time / total_time

    # if pipelining, calculate the number of packets that can be sent with the given window size
    pipelined_packet_count = 1  # default is one packet, because pipelining is optional for this function
    if window_size is not None:
        pipelined_packet_count = window_size / packet_length

    # account for pipelining (if not using pipelining, this just multiplies by 1)
    utilization *= pipelined_packet_count

    return utilization


def main():
    # =============
    # set test data
    # =============
    known_data = {
        'length_in_bytes': 1000,
        'rate_in_Mbps': 1000,
        'rtt_in_ms': 15 * 2
    }
    window_size_in_bytes = 5020  # set to None if not pipelining

    # how many digits --after-- the decimal point should the answers be?
    percentage_precision = 3
    raw_precision = 5

    # =============
    # use test data
    # =============
    # get transmission time by itself
    transmission_time_in_ms = calculate_transmission_time(known_data['length_in_bytes'], known_data['rate_in_Mbps'])
    print(f'\ntransmission time: {transmission_time_in_ms}ms')

    # get utilization
    utilization_in_decimal = round(calculate_network_utilization(known_data, window_size_in_bytes), raw_precision)
    utilization_percentage = round(utilization_in_decimal * 100, percentage_precision)
    print(f'\nutilization time: {utilization_in_decimal}, which is {utilization_percentage}%')


if __name__ == '__main__':
    main()
