from Protocol.Commands.Client.LogicSelectSkinCommand import LogicSelectSkinCommand
from Protocol.Commands.Client.LogicSetPlayerThumbnailCommand import LogicSetPlayerThumbnailCommand
from Protocol.Commands.Client.LogicSetPlayerNameColorCommand import LogicSetPlayerNameColorCommand
from Protocol.Commands.Client.LogicPurchaseDoubleCoinsCommand import LogicPurchaseDoubleCoinsCommand
from Protocol.Commands.Client.LogicPurchaseHeroLvlUpMaterialCommand import LogicPurchaseHeroLvlUpMaterialCommand
from Protocol.Commands.Client.LogicPurchaseOfferCommand import LogicPurchaseOfferCommand
from Protocol.Commands.Client.LogicGatchaCommand import LogicGatchaCommand
from Protocol.Commands.Client.LogicLevelUpCommand import LogicLevelUpCommand

class LogicCommandManager:
    commands = {
       217: "LogicProLeagueSeasonChangedCommand",
       504: "LogicSendAllianceMailCommand",
       221: "LogicTeamChatMuteStateChangedCommand",
       215: "LogicSetSupportedCreatorCommand",
       519: LogicPurchaseOfferCommand,
       539: "LogicBrawlPassAutoCollectWarningSeenCommand",
       541: "LogicClearESportsHubNotificationCommand",
       211: "LogicOffersChangedCommand",
       209: "LogicKeyPoolChangedCommand",
       202: "LogicDiamondsAddedCommand",
       527: LogicSetPlayerNameColorCommand,
       517: "LogicClaimRankUpRewardCommand",
       218: "LogicBrawlPassSeasonChangedCommand",
       528: "LogicViewInboxNotificationCommand",
       536: "LogicPurchaseBrawlPassProgressCommand",
       205: "LogicDecreaseHeroScoreCommand",
       507: "LogicUnlockSkinCommand",
       542: "LogicSelectGroupSkinCommand",
       204: "LogicDayChangedCommand",
       526: "LogicUnlockFreeSkinsCommand",
       525: "LogicSelectCharacterCommand",
       531: "LogicCancelPurchaseOfferCommand",
       524: "LogicVideoStartedCommand",
       522: "LogicHeroSeenCommand",
       214: "LogicGemNameChangeStateChangedCommand",
       206: "LogicAddNotificationCommand",
       515: "LogicClearShopTickersCommand",
       535: "LogicClaimTailRewardCommand",
       512: "LogicToggleInGameHintsCommand",
       203: "LogicGiveDeliveryItemsCommand",
       523: "LogicClaimAdRewardCommand",
       505: LogicSetPlayerThumbnailCommand,
       210: "LogicIAPChangedCommand",
       208: "LogicTransactionsRevokedCommand",
       201: "LogicChangeAvatarNameCommand",
       511: "LogicHelpOpenedCommand",
       521: LogicPurchaseHeroLvlUpMaterialCommand,
       506: LogicSelectSkinCommand,
       520: LogicLevelUpCommand,
       508: "LogicChangeControlModeCommand",
       514: "LogicDeleteNotificationCommand",
       212: "LogicPlayerDataChangedCommand",
       216: "LogicCooldownExpiredCommand",
       540: "LogicPurchaseChallengeLivesCommand",
       213: "LogicInviteBlockingChangedCommand",
       529: "LogicSelectStarPowerCommand",
       503: "LogicClaimDailyRewardCommand",
       509: LogicPurchaseDoubleCoinsCommand,
       537: "LogicVanityItemSeenCommand",
       532: "LogicItemSeenCommand",
       530: "LogicSetPlayerAgeCommand",
       207: "LogicChangeResourcesCommand",
       1000: "LogicDebugCommand",
       500: LogicGatchaCommand,
       222: "LogicRankedSeasonChangedCommand",
       223: "LogicCooldownAddedCommand",
    }

    @classmethod
    def commandExists(cls, commandID: int) -> bool:
        return commandID in cls.commands.keys()

    @classmethod
    def getCommandName(cls, commandID: int) -> str:
        if cls.commandExists(commandID):
            try:
                command = cls.commands[commandID]
            except:
                command = str(commandID)

            if isinstance(command, str): return command

            return command.__class__.__name__
        else: return ""

    @classmethod
    def createCommandByType(cls, commandID: int):
        if cls.commandExists(commandID):
            if not isinstance(cls.commands.get(commandID), str):
                return cls.commands[commandID]

        return

    @staticmethod
    def isServerToClient(commandID: int) -> bool:
        if 200 <= commandID < 500: return True
        elif 500 <= commandID: return False
