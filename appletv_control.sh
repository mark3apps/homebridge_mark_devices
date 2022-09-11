#!/bin/bash

set -e

# Exit immediately for unbound variables.
set -u

length=$#
device=""
io=""
characteristic=""
option=""

ATV_id="9C:3E:53:0E:AE:D8"
airplay_credentials="c7bec8d93fb555809b5d50ba9549463c67df1152d806ac377781f9e313fbb401:640c269421412171c5b462fa08de797b47ae0ef6418c6d9858db38b29293f234:44394134443041362d333735362d343244382d413045452d324538323342443430373430:30353530613130632d393464652d343433652d616139362d376562643135636635396637"
companion_credentials="c7bec8d93fb555809b5d50ba9549463c67df1152d806ac377781f9e313fbb401:e1ec9d12b824582bde069c1f45e6ffecdb83ee66885281cba0a5a9f49ab4e88a:44394134443041362d333735362d343244382d413045452d324538323342443430373430:66663165366439342d326534352d346131372d386163652d373137636361653562313861"

ATV_id2="D0:03:4B:34:86:83"
airplay_credentials2="908aec60016745a07e1f2e0b14a3b9bc68de277d85dee459b8f0237e4cd1ac86:b3eade1449d09c7238e20392901258c72da48eb45028b8cc4c6d00e20f655803:36433735303331432d414141352d344142452d394136462d374338443042423144433736:62393232356137322d333561312d343133332d393461342d383761383061396233393530"
companion_credentials2="908aec60016745a07e1f2e0b14a3b9bc68de277d85dee459b8f0237e4cd1ac86:28f82c989d0dae67405f5ef5c1cdc1874cf98dcf1da67390a5fc141a0850a55f:36433735303331432d414141352d344142452d394136462d374338443042423144433736:63393432643535652d643961332d343465632d393461382d636165306633633364376364"

atvremote_path="/usr/local/bin/"

if [ $length -le 1 ]; then
    printf 'Usage: %s Get < AccessoryName > < Characteristic >\n' "$0"
    printf 'Usage: %s Set < AccessoryName > < Characteristic > < Value >\n' "$0"
    exit 10
fi

if [ $length -ge 1 ]; then
    io=$1
    #  printf "io=$io\n"   # debug
fi
if [ $length -ge 2 ]; then
    device=$2
    #  printf "device = ${device}\n"   # debug
fi
if [ $length -ge 3 ]; then
    characteristic=$3
    #  printf "Characteristic = ${characteristic}\n"   # debug
fi
if [ $length -ge 4 ]; then
    option=$4
    printf "option = %s\n" "${option}" # debug
fi

if [ "${io}" == "Get" ]; then
    case $device in
    'Bed Room TV Power')
        case $characteristic in
        'On')
            # Get Apple TV power state
            ATV_POWER_STATE=$(${atvremote_path}atvremote --id ${ATV_id2} --airplay-credentials ${airplay_credentials2} power_state)
            if [ "${ATV_POWER_STATE}" = "PowerState.On" ]; then
                printf "TRUE\n"
            else
                printf "FALSE\n"
            fi
            exit 0
            ;;
        *)
            printf 'UnHandled Get %s Characteristic %s\n' "${device}" "${characteristic}"
            exit 10
            ;;
        esac
        exit 0
        ;;

    'Living Room TV Power')
        case $characteristic in
        'On')
            # Get Apple TV power state
            ATV_POWER_STATE=$(${atvremote_path}atvremote --id ${ATV_id} --airplay-credentials ${airplay_credentials} power_state)
            if [ "${ATV_POWER_STATE}" = "PowerState.On" ]; then
                printf "TRUE\n"
            else
                printf "FALSE\n"
            fi
            exit 0
            ;;
        *)
            printf 'UnHandled Get %s Characteristic %s\n' "${device}" "${characteristic}"
            exit 10
            ;;
        esac
        exit 0
        ;;

    'Bed Room TV Playing')
        case $characteristic in
        'On')
            # Get Apple TV play status and media type
            ATV_PLAYING=$(${atvremote_path}atvremote --id ${ATV_id2} --airplay-credentials ${airplay_credentials2} playing)
            ATV_PLAYING_STATE=$(echo "$ATV_PLAYING" | grep -oP '(?<=Device state: ).*')
            ATV_MEDIA_PLAYING=$(echo "$ATV_PLAYING" | grep -oP '(?<=Media type: ).*')

            if [ "${ATV_MEDIA_PLAYING}" = "Video" ]; then
                if [ "${ATV_PLAYING_STATE}" = "Playing" ]; then
                    printf "TRUE\n"
                else
                    printf "FALSE\n"
                fi
            elif [ "${ATV_MEDIA_PLAYING}" = "Unknown" ]; then
                if [ "${ATV_PLAYING_STATE}" = "Playing" ]; then
                    printf "TRUE\n"
                else
                    printf "FALSE\n"
                fi
            fi
            exit 0
            ;;
        *)
            printf 'UnHandled Get %s Characteristic %s\n' "${device}" "${characteristic}"
            exit 10
            ;;
        esac
        exit 0
        ;;

    'Living Room TV Playing')
        case $characteristic in
        'On')
            # Get Apple TV play status and media type
            ATV_PLAYING=$(${atvremote_path}atvremote --id ${ATV_id} --airplay-credentials ${airplay_credentials} playing)
            ATV_PLAYING_STATE=$(echo "$ATV_PLAYING" | grep -oP '(?<=Device state: ).*')
            ATV_MEDIA_PLAYING=$(echo "$ATV_PLAYING" | grep -oP '(?<=Media type: ).*')
            if [ "${ATV_MEDIA_PLAYING}" = "Video" ]; then
                if [ "${ATV_MEDIA_PLAYING}" = "Video" ]; then
                    if [ "${ATV_PLAYING_STATE}" = "Playing" ]; then
                        printf "TRUE\n"
                    else
                        printf "FALSE\n"
                    fi
                elif [ "${ATV_MEDIA_PLAYING}" = "Unknown" ]; then
                    if [ "${ATV_PLAYING_STATE}" = "Playing" ]; then
                        printf "TRUE\n"
                    else
                        printf "FALSE\n"
                    fi
                fi
            else
                printf "FALSE\n"
            fi
            exit 0
            ;;
        *)
            printf 'UnHandled Get %s Characteristic %s\n' "${device}" "${characteristic}"
            exit 10
            ;;
        esac
        exit 0
        ;;
    *)
        printf 'UnHandled Get %s Characteristic %s\n' "${device}" "${characteristic}"
        exit 10
        ;;
    esac
fi
if [ "${io}" == 'Set' ]; then
    case $device in
    'Living Room TV Power')
        case $characteristic in
        'On')
            # Get Apple TV current power state and switch accordingly
            ATV_POWER_STATE=$(${atvremote_path}atvremote --id ${ATV_id} --airplay-credentials ${airplay_credentials} power_state)

            if [ "${ATV_POWER_STATE}" != "PowerState.On" ] && [ "${option}" = "1" ]; then
                ${atvremote_path}atvremote --id ${ATV_id} --companion-credentials ${companion_credentials} turn_on
            elif [ "${ATV_POWER_STATE}" == "PowerState.On" ] && [ "${option}" = "0" ]; then
                ${atvremote_path}atvremote --id ${ATV_id} --companion-credentials ${companion_credentials} turn_off
            fi

            exit 0
            ;;
        *)
            printf 'UnHandled Set %s Characteristic %s\n' "${device}" "${characteristic}"
            exit 10
            ;;
        esac
        exit 0
        ;;

    'Living Room TV Playing')
        case $characteristic in
        'On')
            # Toggle between play and pause
            ${atvremote_path}atvremote --id ${ATV_id} --airplay-credentials ${airplay_credentials} play_pause
            exit 0
            ;;
        *)
            printf 'UnHandled Set %s Characteristic %s\n' "${device}" "${characteristic}"
            exit 10
            ;;
        esac
        exit 0
        ;;

    'Bed Room TV Power')
        case $characteristic in
        'On')
            # Get Apple TV current power state and switch accordingly
            ATV_POWER_STATE=$(${atvremote_path}atvremote --id ${ATV_id2} --airplay-credentials ${airplay_credentials2} power_state)

            if [ "${ATV_POWER_STATE}" != "PowerState.On" ] && [ "${option}" = "1" ]; then
                ${atvremote_path}atvremote --id ${ATV_id2} --companion-credentials ${companion_credentials2} turn_on
            elif [ "${ATV_POWER_STATE}" == "PowerState.On" ] && [ "${option}" = "0" ]; then
                ${atvremote_path}atvremote --id ${ATV_id2} --companion-credentials ${companion_credentials2} turn_off
            fi

            exit 0
            ;;
        *)
            printf 'UnHandled Set %s Characteristic %s\n' "${device}" "${characteristic}"
            exit 10
            ;;
        esac
        exit 0
        ;;

    'Bed Room TV Playing')
        case $characteristic in
        'On')
            # Toggle between play and pause
            ${atvremote_path}atvremote --id ${ATV_id2} --airplay-credentials ${airplay_credentials2} play_pause
            exit 0
            ;;
        *)
            printf 'UnHandled Set %s Characteristic %s\n' "${device}" "${characteristic}"
            exit 10
            ;;
        esac
        exit 0
        ;;
    *)
        printf 'UnHandled Get %s Characteristic %s\n' "${device}" "${characteristic}"
        exit 10
        ;;
    esac
fi
printf 'Unknown io command %s\n' "${io}"
exit 10
